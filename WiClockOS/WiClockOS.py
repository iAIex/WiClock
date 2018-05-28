# -*- coding: cp1252 -*-
import os
import time
from copy import deepcopy
import platform
from threading import Thread
import threading
import classes
import sys
import psutil
import Queue
import signal


class SharedInformation():
    SELF = 0

    def __init__(self):
        if SharedInformation.SELF != 0:
            pass
        else:
            SharedInformation.SELF = self

        # refresh rate of the clock
        self.UPDATE_TIME = 0.1

        # Threading values
        self.THREADS = {}  # here all threads are stayed with {t_name:[t_name, t_type, t_class]}
        # the queue for inter thread communication, every thread has it own namespace and queue
        self.threading_queue = {}  # format: {to_thread_name:Queue([sender, data], [sender, data]) ... }

        # debug variables, turn DEBUG to 1 to get debug messeges
        self.DEBUG = 0
        self.DEBUG_STRINGS = {}

        # width and height of the wotch on pixel
        self.width = 32
        self.height = 8
        self.ACTIVE_MODULES = {}
        # the display buffer in pixel data
        self.DisplayBuffer = [[[0, 0, 0] for x in xrange(self.height)] for x1 in xrange(self.width)]
        # brighness of the display in range 0 to 15
        self.brightness = 0

        # here events get pulled in and will be handled by the event mgr
        self.ACTIONS = []
        # this value defines the active widget
        self.Active_widget = 0
        # number of widgets
        self.widget_number = 0

        # the namespace for the values
        self.MOD_VARIABLES = {}
        # the gpio number of the buttons of the raspberry
        self.BINDED_GPIOS = {14: "LEFT", 15: "HOME", 18: "RIGHT"}

        # set the driver name for redraw event
        self.driver_name = ""


class ThredingMonitor():
    # This class is monitoing all logged threads
    MONITORING = []

    def __init__(self, SharedInformation):
        self.SharedInformation = SharedInformation
        time.sleep(1)

        self.SharedInformation.threading_queue["ThreadingMonitor"] = Queue.Queue()

        monitor_thread = Thread(target=self.run)
        monitor_thread.daemon = True
        monitor_thread.start()
        monitor_thread.setName("ThreadingMonitor")

    @staticmethod
    def restart_program():

        python = sys.executable
        os.execl(python, python, *sys.argv)
        # os.system("python widgets.py")

    def run(self):
        while True:
            for key in self.SharedInformation.THREADS:
                state = self.SharedInformation.THREADS[key][2].is_alive()
                if state != True:
                    self.restart_program()
            time.sleep(2)


class AddonMgr():
    # starts and handles the addons in single threads
    def __init__(self, SharedInformation):
        self.SharedInformation = SharedInformation
        self.init_addons()

    def init_addons(self):
        addon_list = os.listdir("addons/")
        self.ADDONS = {}
        for addon in addon_list:
            filename = "addons/" + addon + "/" + addon + ".py"

            directory, addon_name = os.path.split(filename)
            addon_name = os.path.splitext(addon_name)[0]

            path = list(sys.path)
            sys.path.insert(0, directory)

            try:
                addon = __import__(addon_name)
            finally:
                sys.path[:] = path
            addon = addon.Addon(self.SharedInformation)
            self.ADDONS[addon_name] = Thread(target=addon.run)
            self.SharedInformation.THREADS[addon_name] = [addon_name, "Addon", self.ADDONS[addon_name]]
            self.SharedInformation.threading_queue[addon_name] = Queue.Queue()
            self.ADDONS[addon_name].daemon = True
            self.ADDONS[addon_name].start()


class ModuleMgr():
    def __init__(self, SharedInformation):
        self.SharedInformation = SharedInformation
        module_list = os.listdir("modules/")
        self.MODULES = {}
        for module in module_list:
            filename = "modules/" + module + "/" + module + ".py"

            directory, module_name = os.path.split(filename)
            module_name = os.path.splitext(module_name)[0]

            path = list(sys.path)
            sys.path.insert(0, directory)
            try:
                self.MODULES[module] = __import__(module_name)
            finally:
                sys.path[:] = path
            self.MODULES[module] = self.MODULES[module].Module(self.SharedInformation)
        self.Module_Thread = Thread(target=self.run)
        self.SharedInformation.threading_queue["ModuleMgr"] = Queue.Queue()
        time.sleep(1)
        self.SharedInformation.THREADS["ModuleMgr"] = ["ModuleMgr", "ModuleMgr", self.Module_Thread]
        self.Module_Thread.daemon = True
        self.Module_Thread.start()

    def run(self):
        time.sleep(1)
        while True:
            for mod in self.MODULES.keys():
                self.SharedInformation.MOD_VARIABLES[mod] = self.MODULES[mod].update()
            time.sleep(self.SharedInformation.UPDATE_TIME)


class DriverMgr():

    def __init__(self, SharedInformation):
        self.SharedInformation = SharedInformation
        if platform.system() == "Linux":
            filename = "driver/MAX7219/MAX7219.py"

            directory, module_name = os.path.split(filename)
            module_name = os.path.splitext(module_name)[0]

            path = list(sys.path)
            sys.path.insert(0, directory)
            try:

                self.driver_module = __import__(module_name)
            finally:
                sys.path[:] = path
        else:
            filename = "driver/simulator/simulator.py"

            directory, module_name = os.path.split(filename)
            module_name = os.path.splitext(module_name)[0]

            path = list(sys.path)
            sys.path.insert(0, directory)
            try:

                self.driver_module = __import__(module_name)
            finally:
                sys.path[:] = path
        self.SharedInformation.driver_name = module_name
        driver_tread = Thread(target=self.run)
        self.name = "DisplayDriver"
        self.SharedInformation.threading_queue["DisplayDriver"] = Queue.Queue()
        self.SharedInformation.driver_name = self.name
        self.SharedInformation.THREADS[module_name] = [module_name, "DisplayDriver", driver_tread]
        driver_tread.daemon = True
        driver_tread.start()

    def run(self):
        time.sleep(1)
        self.DRIVER = self.driver_module.driver(self.SharedInformation)
        self.DRIVER.set(self.SharedInformation.DisplayBuffer)
        self.DRIVER.draw()
        while True:
            id = self.SharedInformation.threading_queue[self.name].get()[1]
            if id == "REDRAW":
                self.DRIVER.set(self.SharedInformation.DisplayBuffer)
                self.DRIVER.draw()
            # time.sleep(self.SharedInformation.UPDATE_TIME)


class ActionMgr():
    def __init__(self, SharedInformation):

        self.SharedInformation = SharedInformation
        action_tread = Thread(target=self.run)
        self.SharedInformation.THREADS["ActionMgr"] = ["ActionMgr", "ActionMgr", action_tread]
        self.SharedInformation.threading_queue["ActionMgr"] = Queue.Queue()
        action_tread.daemon = True
        action_tread.start()

    def run(self):
        time.sleep(1)
        while True:
            id = self.SharedInformation.threading_queue["ActionMgr"].get()[1]
            print id
            if id == "LEFT":
                self.SharedInformation.Active_widget = self.SharedInformation.Active_widget - 1
                if self.SharedInformation.Active_widget < 0:
                    self.SharedInformation.Active_widget = 0
            elif id == "HOME":
                self.SharedInformation.Active_widget = 0
            elif id == "RIGHT":
                self.SharedInformation.Active_widget = self.SharedInformation.Active_widget + 1
                if self.SharedInformation.Active_widget >= self.SharedInformation.widget_number:
                    self.SharedInformation.Active_widget = self.SharedInformation.widget_number - 1


class StartClockOS():

    def __init__(self, widget_list):
        self.SharedInformation = SharedInformation()
        self.DEBUG = self.SharedInformation.DEBUG

        ModuleMgr(self.SharedInformation)
        AddonMgr(self.SharedInformation)
        ActionMgr(self.SharedInformation)
        DriverMgr(self.SharedInformation)
        ThredingMonitor(self.SharedInformation)

        self.widget_list = widget_list
        self.WIDGETS = []

        width = self.SharedInformation.width
        height = self.SharedInformation.height

        print "--- - - -      WiClockOS v. 1.0 - (C) Bastian Frey 2018      - - - ---"

        self.WINTER = classes.WidgetInterpreter(self.SharedInformation)

        for wname in self.widget_list:
            self.WIDGETS.append(classes.Widget(self.SharedInformation, wname))

        self.SharedInformation.widget_number = len(self.WIDGETS)


    def run(self):
        active = self.SharedInformation.Active_widget
        widget_data = self.WIDGETS[active].update()

        self.SharedInformation.DisplayBuffer = self.WINTER.interpret(widget_data,
                                                                     self.widget_list[active])
        self.SharedInformation.threading_queue[self.SharedInformation.driver_name].put(
            ["DisplayDriver", "REDRAW"])

        active_old = -1
        while True:
            t = time.time()

            active = self.SharedInformation.Active_widget

            widget_data = self.WIDGETS[active].update()

            if active_old != active:
                widget_data = self.WIDGETS[active].update(1)
                active_old = active


            if len(widget_data) != 0 and active_old == active:
                self.SharedInformation.DisplayBuffer = self.WINTER.interpret(widget_data,
                                                                             self.widget_list[active])

                self.SharedInformation.threading_queue[self.SharedInformation.driver_name].put(
                    ["DisplayDriver", "REDRAW"])

            self.debug()
            time.sleep(self.SharedInformation.UPDATE_TIME)

    def debug(self):
        if self.SharedInformation.DEBUG == 1:
            print
            print ">> CPU-Workload: ", psutil.cpu_percent()
            print ">> INTERPRETATION ERRORS: ", self.WINTER.ERROR
            print ">> ACTIVE WIDGET: ", self.widget_list[self.SharedInformation.Active_widget]
            # print ">> ",self.SharedInformation.THREADS
            for key in self.SharedInformation.DEBUG_STRINGS.keys():
                print ">>", key, ":", self.SharedInformation.DEBUG_STRINGS[key]





