# -*- coding: cp1252 -*-
import sys

import imp
import os
import time
import atexit
from copy import deepcopy
import platform

import classes


class WidgetMgr():
    ACTIVE = 0
    WIDGET_NUMBERS = 0
    # 0:width, 1:height, 2:Brightness
    DISPLAY_INFOS = [32, 8, 15]
    def __init__(self, widget_list):
        self.DEBUG = 1
        self.widget_list = widget_list
        self.WIDGETS = []
        width = self.DISPLAY_INFOS[0]
        height = self.DISPLAY_INFOS[1]
        print "--- - - -      WiClockOS v. 1.0 - (C) Bastian Frey 2018      - - - ---"

        if platform.system() == "Linux":
            filename = "driver/MAX7219/MAX7219.py"

            directory, module_name = os.path.split(filename)
            module_name = os.path.splitext(module_name)[0]

            path = list(sys.path)
            sys.path.insert(0, directory)
            try:
                driver_module = __import__(module_name)
            finally:
                sys.path[:] = path
        else:
            filename = "driver/simulator/simulator.py"

            directory, module_name = os.path.split(filename)
            module_name = os.path.splitext(module_name)[0]

            path = list(sys.path)
            sys.path.insert(0, directory)
            try:
                driver_module = __import__(module_name)
            finally:
                sys.path[:] = path

        self.DRIVER = driver_module.driver(self, width, height)
        self.WINTER = classes.WidgetInterpreter(width, height)
        self.init_addons()
        self.init_modules()
        for addon in self.ADDONS.keys():
            self.ADDONS[addon].update()
        for module in self.MODULES.keys():
            self.MODULES[module].update()

        for wname in self.widget_list:
            self.WIDGETS.append(classes.Widget(wname, self.ADDONS, self.MODULES))

        WidgetMgr.WIDGET_NUMBERS = len(self.WIDGETS)

    def display_update(self):
        for addon in self.ADDONS.keys():
            self.ADDONS[addon].update()
        for module in self.MODULES.keys():
            self.MODULES[module].update()
        t = time.time()
        active = WidgetMgr.ACTIVE
        self.WIDGETS[active].update()

        self.WINTER.interpret(self.WIDGETS[active].get(), self.widget_list[active])
        self.DRIVER.set(self.WINTER.PIXEL_BUFFER)
        self.DRIVER.draw()

        if self.DEBUG == 1:
            print
            print ">> CPU-Workload: ", int((time.time() - t) * 100), " %"
            print ">> INTERPRET ERRORS: ", self.WINTER.ERROR
            print ">> ACTIVE WIDGET: ", self.widget_list[self.ACTIVE]

        # time.sleep(0.25 - (time.time() - t))

    def init_addons(self):
        addon_list = os.listdir("addons/")
        print addon_list
        self.ADDONS = {}
        for addon in addon_list:
            filename = "addons/" + addon + "/" + addon + ".py"

            directory, module_name = os.path.split(filename)
            module_name = os.path.splitext(module_name)[0]

            path = list(sys.path)
            sys.path.insert(0, directory)
            try:
                self.ADDONS[addon] = __import__(module_name)
            finally:
                sys.path[:] = path
            self.ADDONS[addon] = self.ADDONS[addon].Addon()

    def init_modules(self):
        module_list = os.listdir("modules/")
        print module_list
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
            self.MODULES[module] = self.MODULES[module].Module()



    @ staticmethod
    def ACTION(id):
        # id = [what kind of action, action]
        if id[0] == "WIDGET":
            if id[1] == "LEFT":
                WidgetMgr.ACTIVE = WidgetMgr.ACTIVE - 1
                if WidgetMgr.ACTIVE < 0:
                    WidgetMgr.ACTIVE = 0
            elif id[1] == "HOME":
                WidgetMgr.ACTIVE = 0
            elif id[1] == "RIGHT":
                WidgetMgr.ACTIVE = WidgetMgr.ACTIVE + 1
                if WidgetMgr.ACTIVE >= WidgetMgr.WIDGET_NUMBERS:
                    WidgetMgr.ACTIVE = WidgetMgr.WIDGET_NUMBERS-1



WiClockOS = WidgetMgr(["basic", "test", "test2"])
while True:

    WiClockOS.display_update()




