import sys

import imp
import os
import time
import atexit
from copy import deepcopy

import classes


class WidgetMgr():
    def __init__(self, widget_list):

        self.WIDGETS = []
        self.active = 0 # which widgetd is active
        self.width = 32
        self.height = 8
        print "--- - - -      WiClockOS v. 1.0 - (C) Bastian Frey 2018      - - - ---"
        filename = "driver/simulator/simulator.py"

        directory, module_name = os.path.split(filename)
        module_name = os.path.splitext(module_name)[0]

        path = list(sys.path)
        sys.path.insert(0, directory)
        try:
            self.driver = __import__(module_name)
        finally:
            sys.path[:] = path  # restore
        self.DRIVER = self.driver.driver()
        self.MOD = classes.Module()
        self.WINTER = classes.WidgetInterpreter(self.width, self.height)
        classes.Widget.GLOBAL_VARS = deepcopy(self.MOD.get())
        for self.wname in widget_list:
            self.WIDGETS.append(classes.Widget(self.wname))


    def display_update(self):
        self.t = time.time()
        classes.Widget.set_module_vars(self.MOD.get())
        self.WIDGETS[self.active].update()
        self.WINTER.interpret(self.WIDGETS[self.active].get())
        self.DRIVER.set(self.WINTER.PIXEL_BUFFER)
        self.DRIVER.draw()
        print ">> Parsing time: ", round(time.time() - self.t, 3), "Sleeping time: ", round(1 - (time.time() - self.t), 3)
        time.sleep(1 - (time.time() - self.t))




a = WidgetMgr(["test"])
while True:
    a.display_update()
    print



