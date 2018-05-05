from copy import deepcopy
import poplib
import time
import os
from datetime import datetime
from datetime import datetime


# Handle Single widget (parsing)
class Widget():
    MODULE_VARS = {}
    GLOBAL_VARS = {}

    def __init__(self, name):
        self.name = name
        self.NAMESPACE = {}
        self.NAMESPACE_ORIGINAL = {}
        self.NAMESPACE_FUSES = {}
        self.TAGS = []
        self.ORIGINAL = []
        self.PARSED = []
        self.namespace = {}

        self.d = open("widgets/"+self.name+"/"+self.name+".ini")
        self.lines = self.d.readlines()
        self.ORIGINAL = deepcopy(self.lines)
        self.d.close()

        self.temp0 = 0
        self.temp1 = 0
        self.temp2 = 0
        self.temp3 = 0

        # line counters:
        self.lc0 = 0
        self.lc1 = 0
        self.lc2 = 0

        self.prepars()
        self.pars_variable()
        self.pars_tags()

        #print self.NAMESPACE
        #print self.TAGS
        #print self.NAMESPACE_FUSES

    def prepars(self):
        # delete empty lines, comments, line numbers for debugging and end-of-line character
        self.i = 0
        self.line_numbers = [self.x for self.x in xrange(1, len(self.lines)+1)]
        while self.i != len(self.lines):
            if self.lines[self.i][0] == "\n" or self.lines[self.i][0] == "#":
                del self.lines[self.i]
                del self.line_numbers[self.i]
            else:
                if self.lines[self.i][-1] == "\n":
                    self.lines[self.i] = self.lines[self.i][0:-1]
                self.i = self.i + 1

        # seperate [TAGS]: be careful, first index in tag is tagname, second is line number, third is the LINE
        self.lc0 = -1
        for self.i in xrange(len(self.lines)):
            if self.lines[self.i][0] == "[":
                self.TAGS.append([[self.line_numbers[self.i], self.lines[self.i], 0, 0]])

                self.lc0 = self.lc0 + 1
            else:
                self.TAGS[self.lc0].append([self.line_numbers[self.i], self.lines[self.i], 0, 0])

        for self.i in xrange(len(self.TAGS)):
            if self.TAGS[self.i][0][1] == "[Variables]":
                for self.ii in xrange(1,  len(self.TAGS[self.i])):
                    self.var_name = self.TAGS[self.i][self.ii][1].split("=")[0]
                    self.var_content = ""
                    self.line = self.TAGS[self.i][self.ii][0]
                    for self.iii in xrange(1, len(self.TAGS[self.i][self.ii][1].split("="))):
                        self.var_content = self.var_content + self.TAGS[self.i][self.ii][1].split("=")[self.iii]
                        if self.iii+1 < len(self.TAGS[self.i][self.ii][1].split("=")):
                            self.var_content = self.var_content + "="
                    self.NAMESPACE[self.var_name] = self.var_content
                    self.NAMESPACE_FUSES[self.var_name] = [self.line, 0, 0, 0, 0]

            if self.TAGS[self.i][0][1] == "[Calculations]":
                for self.ii in xrange(1, len(self.TAGS[self.i])):
                    self.var_name = self.TAGS[self.i][self.ii][1].split("=")[0]
                    self.var_content = ""
                    self.line = self.TAGS[self.i][self.ii][0]
                    for self.iii in xrange(1, len(self.TAGS[self.i][self.ii][1].split("="))):
                        self.var_content = self.var_content + self.TAGS[self.i][self.ii][1].split("=")[self.iii]
                        if self.iii + 1 < len(self.TAGS[self.i][self.ii][1].split("=")):
                            self.var_content = self.var_content + "="
                    self.NAMESPACE[self.var_name] = self.var_content
                    self.NAMESPACE_FUSES[self.var_name] = [self.line, 1, 0, 0, 0]
        self.lc0 = 0
        for self.i in xrange(len(self.TAGS)):
            if self.TAGS[self.i - self.lc0][0][1] == "[Variables]":
                del self.TAGS[self.i - self.lc0]
                self.lc0 = self.lc0 + 1

            if self.TAGS[self.i - self.lc0][0][1] == "[Calculations]":
                del self.TAGS[self.i - self.lc0]
                self.lc0 = self.lc0 + 1

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
        self.key = key
        self.cc = True
        self.temp0 = find_strings(self.NAMESPACE[self.key], "$")

        while self.cc:
            # Value stuff

            self.cc = False
            if len(self.temp0) > 1:

                self.glob_name = self.NAMESPACE[self.key][self.temp0[0] + 1:self.temp0[1]]

                try:
                    if self.glob_name[0] != "*" and self.glob_name[-1] != "*":
                        Widget.GLOBAL_VARS[self.glob_name]
                    else:
                        self.glob_name = "##"
                except:
                    self.glob_name = "##"

                if self.glob_name != "##":
                    self.NAMESPACE[self.key] = self.NAMESPACE[self.key][:self.temp0[0]] + Widget.GLOBAL_VARS[self.glob_name] + self.NAMESPACE[self.key][self.temp0[1] + 1:]
                    self.cc = True
                    self.temp0 = find_strings(self.NAMESPACE[self.key], "$")

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

    def pars_tags(self):
        self.PARSED = []
        for self. i in xrange(len(self.TAGS)):
            self.tag = []
            for self.ii in xrange(len(self.TAGS[self.i])):

                self.temp0 = find_strings(self.TAGS[self.i][self.ii][1], "#")
                self.temp1 = find_strings(self.TAGS[self.i][self.ii][1], "$")

                self.cc = True
                self.ccc = 0


                while self.cc:
                    self.cc = False
                    self.ccc = 0

                    if len(self.temp0) > 1 and self.ii != 0:
                        self.var_name = self.TAGS[self.i][self.ii][1][self.temp0[0]+1:self.temp0[1]]
                        if len(self.var_name) > 0 and self.var_name[0] != "*" and self.var_name[-1] != "*" and self.var_name in self.NAMESPACE:
                            self.TAGS[self.i][self.ii][1] = self.TAGS[self.i][self.ii][1][:self.temp0[0]] + \
                                                            self.NAMESPACE[self.var_name] + self.TAGS[self.i][self.ii][1][self.temp0[1]+1:]
                            self.temp0 = find_strings(self.TAGS[self.i][self.ii][1], "#")
                            self.temp1 = find_strings(self.TAGS[self.i][self.ii][1], "$")
                        else:
                            del self.temp0[0]
                        self.ccc = self.ccc + 1

                    if len(self.temp1) > 1 and self.ii != 0:
                        self.glob_name = self.TAGS[self.i][self.ii][1][self.temp1[0] + 1:self.temp1[1]]

                        if len(self.glob_name) > 0 and self.glob_name[0] != "*" and self.glob_name[-1] != "*" and self.glob_name in Widget.GLOBAL_VARS:

                            self.TAGS[self.i][self.ii][1] = self.TAGS[self.i][self.ii][1][:self.temp1[0]] + \
                                                            Widget.GLOBAL_VARS[self.glob_name] + self.TAGS[self.i][self.ii][
                                                                                                1][self.temp1[1] + 1:]

                            self.temp0 = find_strings(self.TAGS[self.i][self.ii][1], "#")
                            self.temp1 = find_strings(self.TAGS[self.i][self.ii][1], "$")
                        else:
                            del self.temp1[0]

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

        self.startx = 0
        self.starty = 0
        self.endx = 0
        self.endy = 0
        self.colour = [0, 0, 0]
        self.con = 0
        self.ERROR = 0

        WidgetInterpreter.PIXEL_BUFFER = [[[0, 0, 0] for x in xrange(self.height)] for x1 in xrange(self.width)]
        WidgetInterpreter.PIXEL_BUFFER1 = [[[0, 0, 0] for x in xrange(self.height)] for x1 in xrange(self.width)]
        self.FONTS = Fonts()

    def interpret(self, parsed):
        WidgetInterpreter.PIXEL_BUFFER = deepcopy(WidgetInterpreter.PIXEL_BUFFER1)
        self.parsed = parsed
        self.ERROR = 0
        for self.i in xrange(len(self.parsed)):
            self.gfx_mgr(self.parsed[self.i])

        print ">> Interpretion ERRORS: ", self.ERROR

    def gfx_mgr(self, tag):
        self.tag = tag
        self.reset()

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
        else:
            print "Interpretation Error: type missing!"

    def gfx_none(self):
        print ">> NONE"
        pass

    def reset(self):
        self.startx = 0
        self.starty = 0
        self.endx = 0
        self.endy = 0
        self.colour = [0, 0, 0]
        self.con = 0
        self.type = 0
        self.radius = 0
        self.filled = 0
        self.x = 0
        self.y = 0

    def gfx_text(self, tag):
        self._tag = tag
        try:

            self.startx = int(self._tag["startx"])
            self.starty = int(self._tag["starty"])
            self.colour = self._tag["colour"].split(",")
            self.text = self._tag["text"]
            self.font_name = self._tag["font"]
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
                            if self.px_data[self.ii][self.iii] != "0":
                                WidgetInterpreter.PIXEL_BUFFER[self.x][self.y] = [int(self.colour[0]), int(self.colour[1]), int(self.colour[2])]
                            self.x = self.x + 1
                        self.y = self.y + 1
                    self.c = self.c + len(self.px_data[0]) + 1
        except:
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

        try:
            self.startx = int(self._tag["startx"])
            self.starty = int(self._tag["starty"])
            self.endx = int(self._tag["endx"])
            self.endy = int(self._tag["endy"])
            self.colour = self._tag["colour"].split(",")
            if self.startx != self.endx:
                self.m = float(self.endy - self.starty) / float(self.endx - self.startx)
                self.t = self.starty - self.m * self.startx

                for self.x in xrange(self.startx, self.endx + 1):
                    WidgetInterpreter.PIXEL_BUFFER[self.x][int(self.m * self.x + self.t)] = [int(self.colour[0]),
                                                                                             int(self.colour[1]),
                                                                                             int(self.colour[2])]
            elif self.startx == self.endx:
                for self.y in xrange(self.starty, self.endy + 1):
                    WidgetInterpreter.PIXEL_BUFFER[self.startx][int(self.y)] = [int(self.colour[0]),
                                                                                int(self.colour[1]),
                                                                                int(self.colour[2])]
        except:
            self.ERROR = self.ERROR + 1
            pass


# defines the global vars for Weidget.class
class Module():
    def __init__(self):
        self.MODULE = {}
        self.dt = datetime.now()
        self.dt.microsecond

    def get(self):
        # time variables
        self.MODULE["secs"] = time.asctime().split()[3].split(":")[2]
        self.MODULE["sec"] = str(int(time.asctime().split()[3].split(":")[2]))
        self.MODULE["hrs"] = time.asctime().split()[3].split(":")[0]
        self.MODULE["hr"] = str(int(time.asctime().split()[3].split(":")[0]))
        self.MODULE["min"] = time.asctime().split()[3].split(":")[1]
        self.MODULE["mins"] = str(time.asctime().split()[3].split(":")[1])
        self.MODULE["day"] = time.asctime().split()[0]
        self.MODULE["mon"] = time.asctime().split()[1]
        self.MODULE["dates"] = time.asctime().split()[2]
        self.MODULE["date"] = str(int(time.asctime().split()[2]))
        self.MODULE["year"] = time.asctime().split()[4]

        return self.MODULE


# managing fonts ( Subclass of WidgetInterpreter)
class Fonts():
    def __init__(self):
        self.font_list = os.listdir("fonts/")
        self.FONTS = {}
        # include custom font parser here ""
        for self.font_name in self.font_list:
            if ".font" in self.font_name:
                self.FONTS[self.font_name.split(".font")[0]] = StandardFont(self.font_name)
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
class StandardFont():
    def __init__(self, name):
        try:
            self.font_name = name
            self.CHARS = {}
            self.path = "fonts/" + self.font_name
            self.w = open(self.path)
            self.lines = self.w.readlines()
            self.w.close()

            for self.line in self.lines:
                self.line = self.line[:-1]
                if self.line != "\n":

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


def find_strings(string, to_find):
    return [i for i in range(len(string)) if string.startswith(to_find, i)]

