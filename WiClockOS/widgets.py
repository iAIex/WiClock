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
    def __init__(self, widget_list):
        # TEST
        self.widget_list = widget_list
        self.WIDGETS = []
        self.active = 0 # which widgetd is active
        self.width = 32
        self.height = 8
        print "--- - - -      WiClockOS v. 1.0 - (C) Bastian Frey 2018      - - - ---"

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

        self.DRIVER = self.driver_module.driver(self)
        self.MOD = classes.Module()
        self.WINTER = classes.WidgetInterpreter(self.width, self.height)
        classes.Widget.GLOBAL_VARS = deepcopy(self.MOD.get())
        for self.wname in widget_list:
            self.WIDGETS.append(classes.Widget(self.wname))
        WidgetMgr.WIDGET_NUMBERS = len(self.WIDGETS)

    def display_update(self):
        self.t = time.time()
        classes.Widget.set_module_vars(self.MOD.get())
        self.active = WidgetMgr.ACTIVE
        self.WIDGETS[WidgetMgr.ACTIVE].update()
        self.WINTER.interpret(self.WIDGETS[self.active].get(), self.widget_list[self.active])
        self.DRIVER.set(self.WINTER.PIXEL_BUFFER)
        self.DRIVER.draw()
        print ">> Parsing time: ", round(time.time() - self.t, 3), "Sleeping time: ", round(1 - (time.time() - self.t), 3)
        #time.sleep(1 - (time.time() - self.t))

    @ staticmethod
    def ACTION(id):
        print id
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
    print



