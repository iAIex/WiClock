# -*- coding: cp1252 -*-
from copy import deepcopy
import poplib
import time
import os
from datetime import datetime
from datetime import datetime
import platform


# Handle Single widget (parsing)
class Widget():
    MODULE_VARS = {}
    GLOBAL_VARS = {}

    def __init__(self, name, ADDONS, MODULES):
        self.ADDONS = ADDONS
        self.MODULES = MODULES
        self.name = name
        self.NAMESPACE = {}
        self.NAMESPACE_ORIGINAL = {}
        self.NAMESPACE_FUSES = {}
        self.TAGS = []
        self.ORIGINAL = []
        self.PARSED = []
        self.namespace = {}

        lines = custom_readlines("widgets/" + self.name + "/" + self.name + ".ini")
        self.ORIGINAL = deepcopy(lines)

        self.prepars(lines)
        self.pars_variable()
        self.pars_tags()

    # reworked
    def prepars(self, lines):
        # delete empty lines, comments, line numbers for debugging and end-of-line character
        i = 0
        line_numbers = [self.x for self.x in xrange(1, len(lines) + 1)]
        while i < len(lines):
            if lines[i] == "" or lines[i][0] == "#":
                del lines[i]
                del line_numbers[i]
            else:
                i = i + 1
        # seperate [TAGS]: be careful, first index in tag is tagname, second is line number, third is the LINE
        lc0 = -1
        for i in xrange(len(lines)):
            if lines[i][0] == "[":
                self.TAGS.append([[line_numbers[i], lines[i], 1, 0]])

                lc0 = lc0 + 1
            else:
                self.TAGS[lc0].append([line_numbers[i], lines[i], 1, 0])

        for i in xrange(len(self.TAGS)):
            if self.TAGS[i][0][1] == "[Variables]":
                for ii in xrange(1, len(self.TAGS[self.i])):
                    var_name = self.TAGS[i][ii][1].split("=")[0]
                    var_content = ""
                    line = self.TAGS[i][ii][0]
                    for iii in xrange(1, len(self.TAGS[i][ii][1].split("="))):
                        var_content = var_content + self.TAGS[i][ii][1].split("=")[iii]
                        if iii + 1 < len(self.TAGS[i][ii][1].split("=")):
                            var_content = var_content + "="
                    self.NAMESPACE[var_name] = var_content
                    self.NAMESPACE_FUSES[var_name] = [line, 0, 0, 0, 0]

            if self.TAGS[i][0][1] == "[Calculations]":
                for ii in xrange(1, len(self.TAGS[i])):
                    var_name = self.TAGS[i][ii][1].split("=")[0]
                    var_content = ""
                    line = self.TAGS[i][ii][0]
                    for iii in xrange(1, len(self.TAGS[i][ii][1].split("="))):
                        var_content = var_content + self.TAGS[i][ii][1].split("=")[iii]
                        if iii + 1 < len(self.TAGS[i][ii][1].split("=")):
                            var_content = var_content + "="
                    self.NAMESPACE[var_name] = var_content
                    self.NAMESPACE_FUSES[var_name] = [line, 1, 0, 0, 0]
        lc0 = 0
        for i in xrange(len(self.TAGS)):
            if self.TAGS[i - lc0][0][1] == "[Variables]":
                del self.TAGS[i - lc0]
                lc0 = lc0 + 1

            if self.TAGS[i - lc0][0][1] == "[Calculations]":
                del self.TAGS[i - lc0]
                lc0 = lc0 + 1

        self.NAMESPACE_ORIGINAL = deepcopy(self.NAMESPACE)  # backup, dont delete !!
        self.TAGS_ORIGINAL = deepcopy(self.TAGS)

    def prepars_variable(self, key):
        self.key = key
        self.cc = True
        self.temp0 = find_strings(self.NAMESPACE[self.key], "#")

        while self.cc:
            # Value stuff

            self.cc = False
            if len(self.temp0) > 1:

                self.var_name = self.NAMESPACE[self.key][self.temp0[0]+1:self.temp0[1]]

                try:
                    if self.var_name[0] != "*" and self.var_name[-1] != "*":
                        self.NAMESPACE[self.var_name]
                    else:
                        self.var_name = "##"
                except:
                    self.var_name = "##"

                if self.var_name != "##":
                    self.NAMESPACE[self.key] = self.NAMESPACE[self.key][:self.temp0[0]] + self.NAMESPACE[self.var_name] + self.NAMESPACE[self.key][self.temp0[1]+1:]
                    self.cc = True
                    self.temp0 = find_strings(self.NAMESPACE[self.key], "#")

                else:
                    del self.temp0[0]
                    self.cc = True
                    if len(self.temp0) == 0:
                        self.cc = False

    def pars_module(self, key):
        self.standard = "basic"
        self.key = key
        self.cc = True
        self.temp0 = find_strings(self.NAMESPACE[self.key], "$")
        while self.cc:
            # Value stuff

            self.cc = False
            if len(self.temp0) > 1:

                self.module = self.NAMESPACE[self.key][self.temp0[0] + 1:self.temp0[1]].split(".")
                if len(self.module) == 1:
                    self.module_name = self.standard
                    self.cmd = self.module[0]

                else:
                    self.module_name = self.module[0]
                    self.cmd = self.module[1]

                try:
                    if self.module_name[0] != "*" and self.module_name[-1] != "*":

                        self.MODULES[self.module_name]

                    else:
                        self.module_name = "$$"
                except:
                    self.module_name = "$$"

                if self.module_name != "$$":
                    self.ret = str(self.MODULES[self.module_name].get(self.cmd))
                    if self.ret == "None":
                        self.NAMESPACE[self.key] = self.NAMESPACE[self.key][:self.temp0[0]] + \
                                                   self.NAMESPACE[self.key][self.temp0[1] + 1:]
                    else:
                        self.NAMESPACE[self.key] = self.NAMESPACE[self.key][:self.temp0[0]] + \
                                                   self.ret + self.NAMESPACE[self.key][self.temp0[1] + 1:]
                    self.cc = True
                    self.temp0 = find_strings(self.NAMESPACE[self.key], "$")

                else:
                    del self.temp0[0]
                    self.cc = True
                    if len(self.temp0) == 0:
                        self.cc = False

    def pars_addon(self, key):
        self.key = key
        self.cc = True
        self.temp0 = find_strings(self.NAMESPACE[self.key], "&")
        while self.cc:
            # Value stuff

            self.cc = False
            if len(self.temp0) > 1:

                self.addon = self.NAMESPACE[self.key][self.temp0[0] + 1:self.temp0[1]].split(".")
                self.addon_name = self.addon[0]
                self.cmd = self.addon[1]

                try:
                    if self.addon_name[0] != "*" and self.addon_name[-1] != "*":
                        self.ADDONS[self.addon_name]

                    else:
                        self.addon_name = "&&"
                except:
                    self.addon_name = "&&"

                if self.addon_name != "&&":
                    self.ret = str(self.ADDONS[self.addon_name].get(self.cmd))
                    if self.ret == "None":
                        self.NAMESPACE[self.key] = self.NAMESPACE[self.key][:self.temp0[0]] + \
                                                   self.NAMESPACE[self.key][self.temp0[1] + 1:]
                    else:
                        self.NAMESPACE[self.key] = self.NAMESPACE[self.key][:self.temp0[0]] + \
                                                   str(self.ADDONS[self.addon_name].get(self.cmd)) + \
                                                   self.NAMESPACE[self.key][self.temp0[1] + 1:]
                    self.cc = True
                    self.temp0 = find_strings(self.NAMESPACE[self.key], "&")

                else:
                    del self.temp0[0]
                    self.cc = True
                    if len(self.temp0) == 0:
                        self.cc = False

    def pars_variable(self):
        for self._key in self.NAMESPACE.keys():

            if self.NAMESPACE_FUSES[self._key][1] == 1:
                self.namespace = {}
                self.prepars_variable(self._key)
                self.pars_module(self._key)
                self.formel = "value=" + self.NAMESPACE[self._key]
                try:
                    exec self.formel in self.namespace
                    self.NAMESPACE[self._key] = str(self.namespace["value"])
                except:
                    print "Execution Error in line ", self.NAMESPACE_FUSES[self._key][0], ": ",  self.ORIGINAL[self.NAMESPACE_FUSES[self._key][0]-1], self.formel

        for self._key in self.NAMESPACE.keys():
            if self.NAMESPACE_FUSES[self._key][1] == 0:
                self.prepars_variable(self._key)
                self.pars_module(self._key)
                self.pars_addon(self._key)

    def pars_tags(self):
        self.PARSED = []
        for self.i in xrange(len(self.TAGS)):
            self.tag = []
            for self.ii in xrange(len(self.TAGS[self.i])):
                if self.TAGS[self.i][self.ii][2] != 0:
                    self.temp0 = find_strings(self.TAGS[self.i][self.ii][1], "#")
                    self.temp1 = find_strings(self.TAGS[self.i][self.ii][1], "$")
                    self.temp2 = find_strings(self.TAGS[self.i][self.ii][1], "&")

                    self.cc = True
                    self.ccc = 0

                    if len(self.temp0) < 2 and len(self.temp1) < 2 and len(self.temp2) < 2:
                        self.TAGS[self.i][self.ii][2] = 0
                    else:

                        while self.cc:
                            self.cc = False
                            self.ccc = 0

                            # VARIABLE PARSING
                            if len(self.temp0) > 1 and self.ii != 0:

                                self.var_name = self.TAGS[self.i][self.ii][1][self.temp0[0]+1:self.temp0[1]]
                                if len(self.var_name) > 0 and self.var_name[0] != "*" and self.var_name[-1] != "*" and self.var_name in self.NAMESPACE:

                                    self.TAGS[self.i][self.ii][1] = self.TAGS[self.i][self.ii][1][:self.temp0[0]] + \
                                                                    self.NAMESPACE[self.var_name] + self.TAGS[self.i][self.ii][1][self.temp0[1]+1:]

                                    self.temp0 = find_strings(self.TAGS[self.i][self.ii][1], "#")
                                    self.temp1 = find_strings(self.TAGS[self.i][self.ii][1], "$")
                                    self.temp2 = find_strings(self.TAGS[self.i][self.ii][1], "&")
                                else:
                                    del self.temp0[0]
                                self.ccc = self.ccc + 1

                                # MODULE PARSING
                            if len(self.temp1) > 1 and self.ii != 0:
                                self.module = self.TAGS[self.i][self.ii][1][self.temp1[0] + 1:self.temp1[1]].split(
                                    ".")
                                if len(self.module) == 1:
                                    self.cmd = self.module[0]
                                    self.module_name = self.standard
                                else:
                                    self.module_name = self.module[0]
                                    self.cmd = self.module[1]

                                if self.module_name in self.MODULES:

                                    self.ret = self.MODULES[self.module_name].get(self.cmd)

                                    if self.ret != None:
                                        self.TAGS[self.i][self.ii][1] = self.TAGS[self.i][self.ii][1][
                                                                        :self.temp1[0]] + \
                                                                        str(self.ret) + \
                                                                        self.TAGS[self.i][self.ii][
                                                                            1][self.temp1[1] + 1:]

                                        self.temp0 = find_strings(self.TAGS[self.i][self.ii][1], "#")
                                        self.temp1 = find_strings(self.TAGS[self.i][self.ii][1], "$")
                                        self.temp2 = find_strings(self.TAGS[self.i][self.ii][1], "&")
                                    else:
                                        self.TAGS[self.i][self.ii][1] = self.TAGS[self.i][self.ii][1][
                                                                        :self.temp1[0]] + \
                                                                        self.TAGS[self.i][self.ii][
                                                                            1][self.temp1[1] + 1:]

                                        self.temp0 = find_strings(self.TAGS[self.i][self.ii][1], "#")
                                        self.temp1 = find_strings(self.TAGS[self.i][self.ii][1], "$")
                                        self.temp2 = find_strings(self.TAGS[self.i][self.ii][1], "&")


                                else:
                                    del self.temp1[0]
                                self.ccc = self.ccc + 1

                            # ADDON PARSING
                            if len(self.temp2) > 1 and self.ii != 0:
                                self.addon = self.TAGS[self.i][self.ii][1][self.temp2[0] + 1:self.temp2[1]].split(".")
                                if self.addon[0] in self.ADDONS:
                                    self.cmd = ""
                                    for self.a in self.addon[1:]:
                                        self.cmd = self.cmd + self.a + "."
                                    self.cmd = self.cmd[:-1]
                                    self.ret = self.ADDONS[self.addon[0]].get(self.cmd)
                                    if self.ret != None:
                                        self.TAGS[self.i][self.ii][1] = self.TAGS[self.i][self.ii][1][:self.temp2[0]] + \
                                                                        str(self.ret) + \
                                                                        self.TAGS[self.i][self.ii][
                                                                            1][self.temp2[1] + 1:]

                                        self.temp0 = find_strings(self.TAGS[self.i][self.ii][1], "#")
                                        self.temp1 = find_strings(self.TAGS[self.i][self.ii][1], "$")
                                        self.temp2 = find_strings(self.TAGS[self.i][self.ii][1], "&")

                                    else:

                                        self.TAGS[self.i][self.ii][1] = self.TAGS[self.i][self.ii][1][:self.temp2[0]] + \
                                                                        self.TAGS[self.i][self.ii][
                                                                            1][self.temp2[1] + 1:]

                                        self.temp0 = find_strings(self.TAGS[self.i][self.ii][1], "#")
                                        self.temp1 = find_strings(self.TAGS[self.i][self.ii][1], "$")
                                        self.temp2 = find_strings(self.TAGS[self.i][self.ii][1], "&")


                                else:
                                    del self.temp2[0]
                                self.ccc = self.ccc + 1

                            if self.ccc != 0:
                                self.cc = True

    def update(self):
        self.NAMESPACE = deepcopy(self.NAMESPACE_ORIGINAL)
        self.TAGS = deepcopy(self.TAGS_ORIGINAL)
        self.pars_variable()
        self.pars_tags()

    def get(self):
        self.update()
        self.PARSED = []
        for self.i in xrange(len(self.TAGS)):
            self.tag = {}
            for self.ii in xrange(len(self.TAGS[self.i])):

                self.line = self.TAGS[self.i][self.ii][1].split("=")
                if len(self.line) > 1:
                    self.str = ""
                    for self.iii in xrange(1, len(self.line)):
                        self.str = self.str + self.line[self.iii] + "="
                    self.str = self.str[0:-1]
                    self.tag[self.line[0]] = self.str

            self.PARSED.append(self.tag)

        self.conditions()
        self.addon_do()
        return self.PARSED

    def conditions(self):
        for self.i in xrange(len(self.PARSED)):
            self.con_string = "IfCondition"
            self.true_string = "IfTrueAction"
            self.false_string = "IfFalseAction"
            self.con_count = 0
            self.cc = True
            self.IfTrue = False
            while self.cc:
                self.cc = False
                self.IfTrue = False
                if self.con_string in self.PARSED[self.i]:
                    if ")&&(" in self.PARSED[self.i][self.con_string]:
                        self.cons = self.PARSED[self.i][self.con_string].split("&&")
                        self.and_count = 0
                        self.and_state = len(self.cons)

                        for self.con in self.cons:
                            if Widget.test_con(self.con[1:-1]) == True:
                                self.and_count = self.and_count + 1
                        if self.and_count == self.and_state:
                            self.IfTrue = True


                    elif ")||(" in self.PARSED[self.i][self.con_string]:
                        self.cons = self.PARSED[self.i][self.con_string].split("||")
                        self.or_count = 0

                        for self.con in self.cons:
                            if Widget.test_con(self.con[1:-1]) == True:
                                self.or_count = self.or_count + 1
                        if self.or_count > 0:
                            self.IfTrue = True
                    else:
                        if Widget.test_con(self.PARSED[self.i][self.con_string][1:-1]) == True:
                            self.IfTrue = True
                        else:
                            self.IfTrue = False
                    self.cc = True
                    del self.PARSED[self.i][self.con_string]
                    if self.IfTrue == True:

                        if self.true_string in self.PARSED[self.i]:
                            self.line = self.PARSED[self.i][self.true_string][1:-1].split("=")
                            self.att = self.line[0]
                            self.do = ""
                            for self.iii in xrange(1, len(self.line)):
                                self.do = self.do + self.line[self.iii] + "="
                            self.do = self.do[0:-1]
                            self.PARSED[self.i][self.att] = self.do
                            del self.PARSED[self.i][self.true_string]
                    else:
                        if self.false_string in self.PARSED[self.i]:
                            self.line = self.PARSED[self.i][self.false_string][1:-1].split("=")
                            self.att = self.line[0]
                            self.do = ""
                            for self.iii in xrange(1, len(self.line)):
                                self.do = self.do + self.line[self.iii] + "="
                            self.do = self.do[0:-1]
                            self.PARSED[self.i][self.att] = self.do
                            del self.PARSED[self.i][self.false_string]



                self.con_count = self.con_count + 1
                self.con_string = "IfCondition" + str(self.con_count)
                self.true_string = "IfTrueAction" + str(self.con_count)
                self.false_string = "IfFalseAction" + str(self.con_count)

    def addon_do(self):
        self.c = 0
        for self.i in xrange(len(self.PARSED)):
            if "type" in self.PARSED[self.i] and self.PARSED[self.i]["type"] == "addon" and "command" in self.PARSED[
                self.i] and "name" in self.PARSED[self.i]:
                if self.PARSED[self.i]["name"] in self.ADDONS:
                    self.ADDONS[self.PARSED[self.i]["name"]].do(self.PARSED[self.i]["command"])
                del self.PARSED[self.i]
                self.i = self.i - 1

    @staticmethod
    def set_module_vars(mod_vars):
        Widget.GLOBAL_VARS = deepcopy(mod_vars)

    @staticmethod
    def test_con(con):

        if ">=" in con:
            con = con.split(">=")
            if len(con) >= 2 and float(con[0]) >= float(con[1]):
                return True
        elif ">" in con:
            con = con.split(">")
            if len(con) >= 2 and float(con[0]) > float(con[1]):
                return True
        elif "<=" in con:
            con = con.split("<=")
            if len(con) >= 2 and float(con[0]) <= float(con[1]):
                return True
        elif "<" in con:
            con = con.split("<")
            if len(con) >= 2 and float(con[0]) < float(con[1]):
                return True
        elif "==" in con:
            con = con.split("==")
            if len(con) >= 2 and str(con[0]) == str(con[1]):
                return True
        elif "!=" in con:
            con = con.split("!=")
            if len(con) >= 2 and str(con[0]) != str(con[1]):
                return True
        return False

# interprets widgets and render for display driver
class WidgetInterpreter():
    PIXEL_BUFFER = []
    PIXEL_BUFFER1 = []

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.ERROR = 0

        WidgetInterpreter.PIXEL_BUFFER = [[[0, 0, 0] for x in xrange(self.height)] for x1 in xrange(self.width)]
        WidgetInterpreter.PIXEL_BUFFER1 = [[[0, 0, 0] for x in xrange(self.height)] for x1 in xrange(self.width)]
        self.FONTS = Fonts()
        self.SOURCES = Sources()

    def interpret(self, parsed, widget_name):
        self.widget_name = widget_name
        WidgetInterpreter.PIXEL_BUFFER = deepcopy(WidgetInterpreter.PIXEL_BUFFER1)
        self.parsed = parsed
        self.ERROR = 0
        for self.i in xrange(len(self.parsed)):
            self.gfx_mgr(self.parsed[self.i])
        # print self.PIXEL_BUFFER
        # print ">> Interpretion ERRORS: ", self.ERROR

    def gfx_mgr(self, tag):
        self.tag = tag
        if "type" in self.tag:

            self.type = self.tag["type"]
            if self.type == "none":
                self.gfx_none()
            elif self.type == "line":
                self.gfx_line(self.tag)
            elif self.type == "point":
                self.gfx_point(self.tag)
            elif self.type == "text":
                self.gfx_text(self.tag)
            elif self.type == "rect":
                self.gfx_rect(self.tag)
            elif self.type == "source":
                self.gfx_src(self.tag)
        else:
            print "Interpretation Error: type missing!"

    def gfx_none(self):
        pass

    def set_options(self, options, tag):
        for self.t in tag.keys():
            # insert here special options like text is a string, colour a list etc
            if self.t == "colour":
                self.col = tag[self.t].split(",")
                options[self.t] == [int(self.col[0]), int(self.col[1]), int(self.col[2])]
            elif self.t == "text":

                self.options[self.t] = tag[self.t]
            else:
                try:
                    self.options[self.t] = int(tag[self.t])
                except ValueError:
                    options[self.t] = tag[self.t]
        return options

    def gfx_text(self, tag):
        self._tag = tag
        self.options = {"startx":0, "starty":0,"colour":[1,1,1], "text":"", "font_name":"default5x3", }
        self.options = self.set_options(self.options, self._tag)
        try:
            self.startx = self.options["startx"]
            self.starty = self.options["starty"]
            self.colour = self.options["colour"]
            self.text = str(self.options["text"])
            self.font_name = self.options["font_name"]
            self.x = self.startx
            self.y = self.starty
            self.c = 0

            for self.i in xrange(len(self.text)):
                self.char = self.text[self.i]
                if self.char == " ":
                    self.char = "SPACE"
                self.px_data = self.FONTS.get_char_from_font(self.font_name, self.char)
                self.y = self.starty

                if self.x < len(self.PIXEL_BUFFER1):
                    for self.ii in xrange(len(self.px_data)):
                        self.x = self.startx + self.c
                        for self.iii in xrange(len(self.px_data[0])):
                            if self.px_data[self.ii][self.iii] != "0" and self.x < self.width and self.y < self.height:
                                WidgetInterpreter.PIXEL_BUFFER[self.x][self.y] = self.colour
                            self.x = self.x + 1
                        self.y = self.y + 1
                    self.c = self.c + len(self.px_data[0]) + 1
        except IOError:
            self.ERROR = self.ERROR + 1
            pass

    def gfx_point(self, tag):
        try:
            self._tag = tag
            self.colour = self._tag["colour"].split(",")
            WidgetInterpreter.PIXEL_BUFFER[int(self._tag["x"])][int(self._tag["y"])] = [int(self.colour[0]),
                                                                                        int(self.colour[1]),
                                                                                        int(self.colour[2])]
        except:
            self.ERROR = self.ERROR + 1
            pass

    def gfx_line(self, tag):
        self._tag = tag
        self.options = {"startx": 0, "starty": 0, "colour": [1, 1, 1], "endx":0, "endy":0}
        self.options = self.set_options(self.options, self._tag)

        try:
            self.startx = self.options["startx"]
            self.starty = self.options["starty"]
            self.endx = self.options["endx"]
            self.endy = self.options["endy"]
            self.colour = self.options["colour"]

            if self.startx != self.endx:
                self.m = float(self.endy - self.starty) / float(self.endx - self.startx)
                self.t = self.starty - self.m * self.startx

                for self.x in xrange(self.startx, self.endx + 1):
                    WidgetInterpreter.PIXEL_BUFFER[self.x][int(self.m * self.x + self.t)] = self.colour
            elif self.startx == self.endx:
                for self.y in xrange(self.starty, self.endy + 1):
                    WidgetInterpreter.PIXEL_BUFFER[self.startx][int(self.y)] = self.colour
        except:
            self.ERROR = self.ERROR + 1
            pass

    def gfx_rect(self, tag):
        self._tag = tag
        self.options = {"startx": 0, "starty": 0, "colour": [1, 1, 1], "endx": 0, "endy": 0, "filled":0}
        self.options = self.set_options(self.options, self._tag)

        try:
            self.startx = self.options["startx"]
            self.starty = self.options["starty"]
            self.endx = self.options["endx"]
            self.endy = self.options["endy"]
            self.colour = self.options["colour"]
            self.filled = self.options["filled"]
            if self.filled == 1:
                for self.x in xrange(self.startx, self.endx):
                    for self.y in xrange(self.starty, self.endy):
                        WidgetInterpreter.PIXEL_BUFFER[self.x][self.y] = self.colour
            else:


                for self.x in xrange(self.startx, self.endx):
                    for self.y in xrange(self.starty, self.endy):

                        if self.x == self.startx or self.x == self.endx-1 or self.y == self.starty or self.y == self.endy-1:
                            WidgetInterpreter.PIXEL_BUFFER[self.x][self.y] = self.colour

        except:
            self.ERROR = self.ERROR + 1

    def gfx_src(self, tag):
        self._tag = tag
        self.options = {"startx": 0, "starty": 0, "source":0, "colour":[1, 1, 1]}
        self.options = self.set_options(self.options, self._tag)
        self.startx = self.options["startx"]
        self.starty = self.options["starty"]
        self.source = self.options["source"]
        self.colour = self.options["colour"]

        if self.source != 0:
            if self.source[0] == "*":
                self.px_data = self.SOURCES.get_widget_source(self.source[1:], self.widget_name)
            else:
                self.px_data = self.SOURCES.get_source(self.source)
            try:
                for self.y in xrange(len(self.px_data)):
                    for self.x in xrange(len(self.px_data[self.y])):
                        self.xx = self.startx + self.x
                        self.yy = self.starty + self.y
                        if self.px_data[self.y][self.x] == 1:
                            self.PIXEL_BUFFER[self.xx][self.yy] = self.colour

            except:
                self.ERROR = self.ERROR + 1

    def gpio_handling(self):
        pass
    def emulated_gpio_handling(self):
        self.MODULE["GPIO0"] = 0
        self.MODULE["GPIO1"] = 0
        self.MODULE["GPIO2"] = 0
        self.MODULE["GPIO3"] = 0
        self.MODULE["GPIO4"] = 0



# managing fonts ( Subclass of WidgetInterpreter)
class Fonts():
    def __init__(self):
        self.font_list = os.listdir("fonts/")
        self.FONTS = {}
        # include custom font parser here ""
        for self.font_name in self.font_list:
            if ".font" in self.font_name:
                self.FONTS[self.font_name.split(".font")[0]] = StandardFontParser(self.font_name)
            elif ".example" in self.font:
                # alternetive parsers !
                pass

        print ">> FONTS initialised!"


    def get_char_from_font(self, font_name, char):
        if font_name in self.FONTS:
            return self.FONTS[font_name].get_char(char)
        else:
            print ">> FONT Error: Font not installed!"
            return 0


# parsing fonts (subclass from Fonts)
class StandardFontParser():
    def __init__(self, name):
        try:
            self.font_name = name
            self.CHARS = {}
            self.path = "fonts/" + self.font_name
            self.lines = custom_readlines(self.path)

            for self.line in self.lines:
                if self.line != "":

                    self.char = self.line.split()[0]
                    self.char_data = self.line.split()[1][1:-1].split(",")
                    self.CHARS[self.char] = self.char_data
        except:
            print ">> FONT INITIALISATION Error: \"%s\"" % self.font_name


    def get_char(self, to_get):
        if to_get in self.CHARS:
            return self.CHARS[to_get]
        elif "ERROR" in self.CHARS:
            return self.CHARS["ERROR"]
        else:
            print ">> CHAR Error: from font \"%s\" char \"%s\" not defined and ERROR char missing!" % (self.font_name, to_get)
            return 0


class Sources():
    def __init__(self):
        self.src_list = os.listdir("sources/")
        self.SOURCES = {}
        self.WIDGET_SOURCES = {}
        # include custom Source parser here ""

        for self.src_name in self.src_list:
            if ".bsrc" in self.src_name:
                self._src_name = self.src_name.split(".")[0]

                self.SOURCES[self._src_name] = self.source_parser(self.src_name)
            elif ".example" in self.src_name:
                # alternetive parsers !
                pass

    def source_parser(self, src_name):

        self.path = "sources/" + src_name
        self.lines = custom_readlines(self.path)

        self.PX_DATA = []

        for self.line in self.lines:

            self.temp0 = find_strings(self.line, "(")
            self.temp1 = find_strings(self.line, ")")
            self. line = self.line[self.temp0[0]+1:self.temp1[0]]

            self.line = self.line.split(",")
            for self.i in xrange(0, len(self.line)):
                self.line[self.i] = int(self.line[self.i])
            self.PX_DATA.append(self.line)
        return self.PX_DATA

    def get_source(self, src_name):
        return self.SOURCES[src_name]

    def get_widget_source(self, src_name, widget_name):
        if widget_name not in self.WIDGET_SOURCES:
            self.path = "widgets/" + widget_name + "/sources/" + src_name + ".bsrc"
            self.lines = custom_readlines(self.path)
            self.PX_DATA = []

            for self.line in self.lines:
                self.line = self.line[1:-1]
                self.line = self.line.split(",")
                for self.i in xrange(0, len(self.line)):
                    self.line[self.i] = int(self.line[self.i])
                self.PX_DATA.append(self.line)
            self.WIDGET_SOURCES[widget_name] = {}
            self.WIDGET_SOURCES[widget_name][src_name] = self.PX_DATA
            return self.PX_DATA
        elif src_name not in self.WIDGET_SOURCES[widget_name]:
            self.path = "widgets/" + widget_name + "/sources/" + src_name + ".bsrc"
            self.lines = custom_readlines(self.path)
            self.PX_DATA = []

            for self.line in self.lines:
                self.line = self.line[1:-2]
                self.line = self.line.split(",")
                for self.i in xrange(0, len(self.line)):
                    self.line[self.i] = int(self.line[self.i])
                self.PX_DATA.append(self.line)
            self.WIDGET_SOURCES[widget_name] = {}
            self.WIDGET_SOURCES[widget_name][src_name] = self.PX_DATA
            return self.PX_DATA

        return self.WIDGET_SOURCES[widget_name][src_name]

def find_strings(string, to_find):
    return [i for i in range(len(string)) if string.startswith(to_find, i)]

def custom_readlines(path):
    w = open(path)
    readlines = w.readlines()
    lines = []
    for line in readlines:
        if "\n" in line and "\r" in line:
            lines.append(line[0:-2])
        elif "\n" in line or "\r" in line:
            lines.append(line[0:-1])
        else:
            lines.append(line)
    w.close()

    return lines


