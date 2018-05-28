# -*- coding: cp1252 -*-
from copy import deepcopy
import poplib
import time
import os
from datetime import datetime
from datetime import datetime
import platform
import copy
import random
import time

VARIABLE_STRING = "#"
MODULE_STRING = "$"

class Run():
    def __init__(self):
        pass

# Handle Single widget (parsing)
class Tag():
    def __init__(self, tag_name):
        self.tag_original = [] # original tag, stores lines for information [[line_number, line], ... ]
        self.tag_name = tag_name # tagname (string)
        self.CONDITIONS = {} # stores all condition of the tag
        self.LINES = []
        self.USED_MOD_VARS ={}
    def pars(self, VARIABLES):
        self.VARIABLES = VARIABLES
        self.SharedInformation = self.VARIABLES.SharedInformation

        # bring LINES to the format
        for LINE in self.tag_original:
            self.LINES.append([LINE[0], seperate_line(LINE[1])[0], seperate_line(LINE[1])[1], 0, [], 0])


        for idx in xrange(len(self.LINES)):
            LINE = self.LINES[idx]
            tmp = find_strings(LINE[2], VARIABLE_STRING)
            tmp1 = find_strings(LINE[2], MODULE_STRING)
            cc = True
            i = 0
            ii = 0
            while cc:
                v_number = 0
                m_number = 0
                if len(tmp) <= 1 and len(tmp1) >= 2:
                    m_number = 0
                    v_number = 99
                elif len(tmp1) <= 1 and len(tmp) >= 2:
                    m_number = 99
                    v_number = 0
                elif len(tmp) <= 1 and len(tmp1) <= 1:
                    m_number = 0
                    v_number = 0
                else:

                    if tmp[0] > tmp1[0]:
                        v_number = 99
                        m_number = 0
                    elif tmp1[0] > tmp[0]:
                        v_number = 0
                        m_number = 99
                    else:
                        v_number = 0
                        m_number = 0


                if v_number < m_number and i < len(tmp)-1:

                    var_name = LINE[2][tmp[i] + 1:tmp[i + 1]]
                    if var_name in self.VARIABLES.NAMESPACE:

                        if self.VARIABLES.NAMESPACE[var_name][2] == 0:
                            LINE[2] = LINE[2][:tmp[i]] + self.VARIABLES.NAMESPACE[var_name][1] + LINE[2][tmp[i+1]+1:]

                        if self.VARIABLES.NAMESPACE[var_name][2] == 1:
                            LINE[2] = LINE[2][:tmp[i]] + "{}" + LINE[2][tmp[i + 1] + 1:]
                            LINE[4].append([0, var_name])
                        tmp = find_strings(LINE[2], VARIABLE_STRING)
                        tmp1 = find_strings(LINE[2], MODULE_STRING)
                        i = -1
                    i = i + 1

                elif m_number < v_number and ii < len(tmp1)-1:
                    mod = LINE[2][tmp1[ii] + 1:tmp1[ii + 1]].split(".")
                    if len(mod) == 2:
                        mod_name = mod[0]
                        mod_var = mod[1]

                        if mod_name in self.SharedInformation.MOD_VARIABLES:
                            if mod_var in self.SharedInformation.MOD_VARIABLES[mod_name]:
                                LINE[2] = LINE[2][:tmp1[ii]] + "{}" + LINE[2][tmp1[ii + 1] + 1:]
                                LINE[4].append([mod_name, mod_var])
                                tmp = find_strings(LINE[2], VARIABLE_STRING)
                                tmp1 = find_strings(LINE[2], MODULE_STRING)
                                if mod_name in self.USED_MOD_VARS:
                                    self.USED_MOD_VARS[mod_name][mod_var] = 0
                                else:
                                    self.USED_MOD_VARS[mod_name] = {}
                                    self.USED_MOD_VARS[mod_name][mod_var] = 0


                                ii = -1
                    ii = ii + 1



                else:
                    cc = False


                self.LINES[idx] = copy.deepcopy(LINE)
        del_list = []
        for idx in xrange(len(self.LINES)):
            LINE = self.LINES[idx]
            if len(LINE[4]) != 0:
                LINE[3] = 1


            self.LINES[idx] = copy.deepcopy(LINE)
            # Condition Handling

            if "IfCondition" in LINE[1] or "IfTrueAction" in LINE[1] or "IfFalseAction" in LINE[1]:

                if "IfCondition" in LINE[1]:
                    C_ID = LINE[1][len("IfCondition"):]
                    if C_ID == "":
                        C_ID = "0"

                    if C_ID in self.CONDITIONS:
                        self.CONDITIONS[C_ID].condition_original = copy.deepcopy(LINE)
                    else:
                        self.CONDITIONS[C_ID] = Condition(self.VARIABLES)
                        self.CONDITIONS[C_ID].condition_original = copy.deepcopy(LINE)
                        self.CONDITIONS[C_ID].tag_name = self.tag_name
                    del_list.append(idx)


                elif "IfTrueAction" in LINE[1]:
                    C_ID = LINE[1][len("IfTrueAction"):]
                    if C_ID == "":
                        C_ID = "0"

                    if C_ID in self.CONDITIONS:
                        self.CONDITIONS[C_ID].trueaction_original = copy.deepcopy(LINE)
                    else:
                        self.CONDITIONS[C_ID] = Condition(self.VARIABLES)
                        self.CONDITIONS[C_ID].trueaction_original = copy.deepcopy(LINE)
                    del_list.append(idx)
                elif "IfFalseAction" in LINE[1]:
                    C_ID = LINE[1][len("IfFalseAction"):]
                    if C_ID == "":
                        C_ID = "0"

                    if C_ID in self.CONDITIONS:
                        self.CONDITIONS[C_ID].falseaction_original = copy.deepcopy(LINE)
                    else:
                        self.CONDITIONS[C_ID] = Condition(self.VARIABLES)
                        self.CONDITIONS[C_ID].falseaction_original = copy.deepcopy(LINE)
                    del_list.append(idx)

        i = 0
        for d in del_list:
            del self.LINES[d-i]
            i = i + 1

        self.pars_conditions()

    def pars_conditions(self):
        for key in self.CONDITIONS.keys():

            self.CONDITIONS[key].pars()
            if self.CONDITIONS[key].type == 0:
                del self.CONDITIONS[key]

    def condition_update(self, TAGS, NAME_LIST):
        for CON in self.CONDITIONS:
            TAGS = self.CONDITIONS[CON].test_condition(TAGS, self.tag_name, NAME_LIST)
            return TAGS


class Condition():
    def __init__(self, Variables):
        self.Variables = Variables
        self.condition_original = []
        self.trueaction_original = []
        self.falseaction_original = []

        self.type = 1
        self.tag_name = 0
        self.CONDITION = []
        self.TRUEACTION =[]
        self.FALSEACTION = []

    def pars(self):
        # just for parsing CONDITION !!
        if len(self.condition_original) == 0:
            type = 0

            return
        self.CONDITION = copy.deepcopy(self.condition_original)
        if ")and(" in self.condition_original[2] and ")or(" in self.condition_original[2]:
            self.type = 0
            return
        elif ")and(" in self.condition_original[2]:
            self.type = "AND"
            self.CONDITION = self.condition_original[2].split(")and(")
        elif ")or(" in self.condition_original[2]:
            self.type = "OR"
            self.CONDITION = self.condition_original[2].split(")or(")
        else:
            self.CONDITION = [self.condition_original[2][:-1]]


        if len(self.trueaction_original) == 0 and len(self.falseaction_original) == 0:
            self.type = 0
            return
        if len(self.CONDITION) == 1:
            self.CONDITION[0] = [self.CONDITION[0][1:], []]
        else:

            self.CONDITION[0] = [self.CONDITION[0][1:], []]
            for i in xrange(1, len(self.CONDITION)-1):
                self.CONDITION[i] = [self.CONDITION[i], []]

            self.CONDITION[-1] = [self.CONDITION[-1][:-1],  []]

        i = 0
        for indx in xrange(len(self.CONDITION)):
            tmp = len(find_strings(self.CONDITION[indx][0], "{}"))
            if tmp > 0:
                for ii in xrange(tmp):
                    self.CONDITION[indx][1].append(self.condition_original[4][i])
                    i = i + 1
        # bring to this format:
        # [ [ [arg1, var1], [arg2, var2] ], type, 0], [ ... ]
        comp = ["==", "!=", "<=", ">=", "<", ">"]

        for indx in xrange(len(self.CONDITION)):
            con = self.CONDITION[indx][0]
            comp_list = []

            for c in comp:
                temp = find_strings(con, c)
                if len(temp) == 0:
                    comp_list.append(99999999)
                else:
                    comp_list.append(temp[0])

            m = min(comp_list)
            type = comp[comp_list.index(m)]
            self.CONDITION[indx].append(type)
            self.CONDITION[indx].append(0)

        # END of CONDITION PARSING: result: [['{}{}', [[0, 'a'], [0, 'c']]], ['{}{}', [[0, 'a'], [0, 'a']]], '==']

        #start TrueAction/FaleAction parsing !
        if self.trueaction_original != []:
            temp = self.trueaction_original[2].split(")(")

            if len(temp) == 1:
                self.TRUEACTION = [[temp[0][1:-1],[] ]]
            else:
                self.TRUEACTION.append([temp[0][1:], []])
                for act in temp[1:-1]:
                    self.TRUEACTION.append([act, [] ])

                self.TRUEACTION.append([temp[-1][:-1], [] ])
            if len(self.trueaction_original[4]) != 0:
                c = 0

                for indx in xrange(len(self.TRUEACTION)):
                    for x in xrange(len(find_strings(self.TRUEACTION[indx][0], "{}"))):
                        self.TRUEACTION[indx][1].append(self.trueaction_original[4][c])
                        c = c + 1

        if self.falseaction_original != []:
            temp = self.falseaction_original[2].split(")(")

            if len(temp) == 1:
                self.FALSEACTION = [[temp[0][1:-1],[] ]]
            else:
                self.FALSEACTION.append([temp[0][1:], []])
                for act in temp[1:-1]:
                    self.FALSEACTION.append([act, [] ])

                self.FALSEACTION.append([temp[-1][:-1], [] ])
            if len(self.falseaction_original[4]) != 0:
                c = 0

                for indx in xrange(len(self.FALSEACTION)):
                    for x in xrange(len(find_strings(self.FALSEACTION[indx][0], "{}"))):
                        self.FALSEACTION[indx][1].append(self.falseaction_original[4][c])
                        c = c + 1

    def test_condition(self, TAGS, TAG_NAMES, NAME_LIST):
        self.TAGS = TAGS
        UPDATED_CONS = []

        for indx in xrange(len(self.CONDITION)):
            CON = self.CONDITION[indx]

            data_list = []
            for data in CON[1]:
                if data[0] == 0:
                    data_list.append(self.Variables.NAMESPACE_CALCULATED[data[1]])
                else:
                    data_list.append(self.Variables.SharedInformation.MOD_VARIABLES[data[0]][data[1]])
            self.CONDITION[indx][3] = CON[0].format(*data_list)

        con_list = []
        for indx in xrange(len(self.CONDITION)):
            con = seperate_line(self.CONDITION[indx][3],self.CONDITION[indx][2])
            con_list.append(compare(con[0], con[1], self.CONDITION[indx][2]))

        TRUTH = False
        if len(con_list) == 1:
            if con_list[0] == True:
                TRUTH = True

        if len(con_list) > 1:
            con = compare(self.type, 0, con_list)
            if con == True:
                TRUTH = True

        if TRUTH == True:
            for instr in self.TRUEACTION:
                data_list = []
                for data in instr[1]:
                    if data[0] == 0:
                        data_list.append(self.Variables.NAMESPACE_CALCULATED[data[1]])
                    else:
                        data_list.append(self.Variables.SharedInformation.MOD_VARIABLES[data[0]][data[1]])

                INSTR = instr[0].format(*data_list)


                INSTR = seperate_line(INSTR)
                ATT = seperate_line(INSTR[0], ".")
                VAL = INSTR[1]
                if ATT[1] == "":
                    tag_name = self.tag_name[1:-1]
                    att = ATT[0]
                    if tag_name in NAME_LIST:
                        idx = NAME_LIST.index(tag_name)
                        TAGS[idx][att] = VAL

                else:
                    tag_name = ATT[0]
                    att = ATT[1]
                    if tag_name in NAME_LIST:
                        idx = NAME_LIST.index(tag_name)
                        TAGS[idx][att] = VAL

        return TAGS


class Variables():
    def __init__(self, SharedInformation):
        self.SharedInformation = SharedInformation
        self.NAMESPACE = {} # {NAME:[line_number, line, variable_flag, module_flag]
        self.NAMESPACE_CALCULATED = {}
        self.USED_MOD_VARS = {}
        self.var_original = [] # this will never ne changed ! and is the original vars [line_number, data]
        self.vars = [] # for parsing only

    def pars(self):
        # bring NAMEPSACE to the given format

        for var in self.var_original:

            try:
                temp = seperate_line(var[1])
                if temp[0][0] != "_":
                    self.NAMESPACE[temp[0]] = [var[0], temp[1], 0, [], 0]
                else:
                    self.NAMESPACE[temp[0][1:]] = [var[0], temp[1], 0, [], -1]

            except:
                pass

        for VAR in self.NAMESPACE:
            # 'aa': [3, '%s%s', 0, [[0, 'b'], [0, 'b']]], 'a': [4, '%s%s%s%2*%s%s%s%s', 0, [[0, 'b'], [0, 'aa'], [0, 'b'], [0, 'c'], [0, 'b'], [0, 'aa'], ['basic', 'sec']]]
            tmp = find_strings(self.NAMESPACE[VAR][1], VARIABLE_STRING)
            tmp1 = find_strings(self.NAMESPACE[VAR][1], MODULE_STRING)
            cc = True
            i = 0
            ii = 0
            while cc:
                cc = False

                first = 1

                # looks if first value is a var or a mod
                if len(tmp) > 1 and i < len(tmp)-1:
                    if len(tmp1) != 0:
                        if tmp[0] > tmp1[0]:
                            first = 0
                            i = i - 1

                    var_string = self.NAMESPACE[VAR][1][tmp[i]:tmp[i+1]+1]
                    var_name = self.NAMESPACE[VAR][1][tmp[i]+1:tmp[i+1]]
                    if var_string != VARIABLE_STRING+VARIABLE_STRING and var_name in self.NAMESPACE and first == 1:

                        self.NAMESPACE[VAR][3].append([0, var_name])
                        self.NAMESPACE[VAR][1] = self.NAMESPACE[VAR][1][:tmp[i]] + "{}" + self.NAMESPACE[VAR][1][tmp[i+1]+1:]
                        tmp = find_strings(self.NAMESPACE[VAR][1], VARIABLE_STRING)
                        tmp1 = find_strings(self.NAMESPACE[VAR][1], MODULE_STRING)
                        i = -1
                        self.NAMESPACE[VAR][2] = 1
                    i = i + 1
                    cc = True

                if len(tmp1) > 1 and ii < len(tmp1)-1:

                    mod_string = self.NAMESPACE[VAR][1][tmp1[ii]:tmp1[ii + 1] + 1]
                    mod_name = self.NAMESPACE[VAR][1][tmp1[ii] + 1:tmp1[ii + 1]].split(".")
                    try:
                        self.SharedInformation.MOD_VARIABLES[mod_name[0]][mod_name[1]]
                        mod = 1
                    except:
                        mod = 0
                    if len(mod_name) > 1 and mod_string != MODULE_STRING + MODULE_STRING and mod == 1:
                        self.NAMESPACE[VAR][3].append(mod_name)
                        self.NAMESPACE[VAR][1] = self.NAMESPACE[VAR][1][:tmp1[ii]] + "{}" + self.NAMESPACE[VAR][1][
                                                                                          tmp1[ii + 1] + 1:]
                        tmp = find_strings(self.NAMESPACE[VAR][1], VARIABLE_STRING)
                        tmp1 = find_strings(self.NAMESPACE[VAR][1], MODULE_STRING)
                        self.NAMESPACE[VAR][2] = 1
                        ii = -1
                    ii = ii + 1
                    cc = True

        for VAR in self.NAMESPACE:
            di = 0
            var_flag = copy.deepcopy(self.NAMESPACE[VAR][3])
            for i in xrange(len(var_flag)):
                var_list = self.NAMESPACE[VAR][3][i - di]
                if var_list[0] == 0:
                    var_name = var_list[1]
                    if self.NAMESPACE[var_name][2] == 0:

                        var_flag[i] = self.NAMESPACE[var_name][1]

                        del self.NAMESPACE[VAR][3][i - di]

                        di = di + 1

                    else:
                        var_flag[i] = "{}"
                else:
                    var_flag[i] = "{}"

            string = self.NAMESPACE[VAR][1]
            self.NAMESPACE[VAR][1] = string.format(*var_flag)
            if len(self.NAMESPACE[VAR][3]) == 0:
                self.NAMESPACE[VAR][2] = 0

        # presolve variable, only mod vars should remain
        for VAR in self.NAMESPACE:
            if self.NAMESPACE[VAR][2] != 0:
                insert_string = []
                flag_list = copy.deepcopy(self.NAMESPACE[VAR][3])
                di = 0
                for i in xrange(len(self.NAMESPACE[VAR][3])):

                    if self.NAMESPACE[VAR][3][i][0] == 0:
                        var_name = self.NAMESPACE[VAR][3][i][1]
                        insert_string.append(self.NAMESPACE[var_name][1])
                        del self.NAMESPACE[VAR][3][i - di]
                        di = di + 1
                        ii = 0

                        for dat in self.NAMESPACE[var_name][3]:
                            self.NAMESPACE[VAR][3].insert(i+ii, dat)
                            ii = ii + 1


                    else:
                        mod_var = self.SharedInformation.MOD_VARIABLES[self.NAMESPACE[VAR][3][i][0]][self.NAMESPACE[VAR][3][i][1]]

                        insert_string.append({})
                self.NAMESPACE[VAR][1] = self.NAMESPACE[VAR][1].format(*insert_string)

        # add used mods to USED_MOD_VARS
        for VAR in self.NAMESPACE:
            if len(self.NAMESPACE[VAR][3]) != 0:
                for mod in self.NAMESPACE[VAR][3]:
                    try:

                        mod_name = mod[0]
                        mod_var = mod[1]
                        self.SharedInformation.MOD_VARIABLES[mod_name][mod_var]
                        if mod_name in self.USED_MOD_VARS:
                            self.USED_MOD_VARS[mod_name][mod_var] = 0
                        else:

                            self.USED_MOD_VARS[mod_name] = {}
                            self.USED_MOD_VARS[mod_name][mod_var] = 0
                    except:
                        pass
        # setting up list for testing:
        # test if var is passible to calculate
        test_array = [random.randint(1,100) for x in xrange(99)]

        for VAR in self.NAMESPACE:
            if self.NAMESPACE[VAR][4] != -1:
                formel = "value=" + self.NAMESPACE[VAR][1].format(*test_array)
                namespace = {}
                try:
                    exec formel in namespace
                    if str(namespace["value"]) != self.NAMESPACE[VAR][1]:
                        if self.NAMESPACE[VAR][2] == 0:
                            self.NAMESPACE[VAR][1] = str(namespace["value"])

                        else:
                            self.NAMESPACE[VAR][4] = 1
                except:
                    pass
            else:
                self.NAMESPACE[VAR][4] = 0

    def calculate_var(self):

        for VAR in self.NAMESPACE:
            insert_list = []
            for mod in self.NAMESPACE[VAR][3]:
                try:
                    mod_name = mod[0]
                    mod_var = mod[1]
                    insert_list.append(self.SharedInformation.MOD_VARIABLES[mod_name][mod_var])
                except:
                    insert_list.append("0")

            if self.NAMESPACE[VAR][4] != 0:

                formel = "value=" + self.NAMESPACE[VAR][1].format(*insert_list)
                namespace = {}
                try:
                    exec formel in namespace
                    self.NAMESPACE_CALCULATED[VAR] = str(namespace["value"])

                except:
                    self.NAMESPACE[VAR][4] = 0

            elif self.NAMESPACE[VAR][4] == 0:
                self.NAMESPACE_CALCULATED[VAR] = str(self.NAMESPACE[VAR][1])



class Widget():

    def __init__(self,SharedInformation, widget_name):

        self.SharedInformation = SharedInformation
        self.widget_name = widget_name
        self.lines = custom_readlines("widgets/" + self.widget_name + "/" + self.widget_name + ".ini")
        self.USED_MOD_VARS = {}

        self.TAG_NAMES = []
        self.VARIABLES = Variables(SharedInformation)
        self.TAGS = []
        # seperate and preorder the lines
        t = time.time()
        self.seperate()

        # pars variables and set static / non static
        self.VARIABLES.pars()
        self.USED_MOD_VARS_var = copy.deepcopy(self.VARIABLES.USED_MOD_VARS)


        t1 = time.time()
        self.VARIABLES.calculate_var()
        for tag in self.TAGS:
            tag.pars(self.VARIABLES)
            self.USED_MOD_VARS_tag = copy.deepcopy(tag.USED_MOD_VARS)

        self.USED_MOD_VARS = merge_two_dicts(self.USED_MOD_VARS_var, self.USED_MOD_VARS_tag)
        # debug information
        #self.debug()

    def seperate(self):
        # this seperates self.lines in Tags and variables, also set the line_numbers
        tags = []
        line_counter = 1
        tag_counter = -1
        for line in self.lines:
            if line != "":
                if line[0] == "[" and line[-1] == "]":
                    tag_counter = tag_counter + 1
                    tags.append([])
                    tags[tag_counter].append([line_counter, line])
                elif line[0] != "#":
                    tags[tag_counter].append([line_counter, line])
            line_counter = line_counter + 1

        for tag in tags:
           #if tag[0][1] == "[Calculations]":
                #self.VARIABLES.var_original = tag[1:]
            if tag[0][1] == "[Variables]":
                self.VARIABLES.var_original = tag[1:]
            else:

                self.TAG_NAMES.append(tag[0][1][1:-1])
                self.TAGS.append(Tag(tag[0][1]))
                self.TAGS[-1].tag_original = tag[1:]

    def debug(self):
        print
        print ">> DEBUG <<"
        # Debug function for programming only
        #print "[Variables] :", self.VARIABLES.var_original
        print self.VARIABLES.NAMESPACE
        print self.VARIABLES.NAMESPACE_CALCULATED

    def update(self, forece_update=0):

        do_update = 0
        for mod_name in self.USED_MOD_VARS:
            for var_name in self.USED_MOD_VARS[mod_name]:
                if self.USED_MOD_VARS[mod_name][var_name] != self.SharedInformation.MOD_VARIABLES[mod_name][var_name]:
                    do_update = 1
        if do_update == 0 and forece_update == 0:
            return []

        for mod_name in self.USED_MOD_VARS:
            for var_name in self.USED_MOD_VARS[mod_name]:
                if self.USED_MOD_VARS[mod_name][var_name] != self.SharedInformation.MOD_VARIABLES[mod_name][var_name]:
                    self.USED_MOD_VARS[mod_name][var_name] = self.SharedInformation.MOD_VARIABLES[mod_name][var_name]

        t = time.time()
        self.VARIABLES.calculate_var()
        updated = []
        for tag in self.TAGS:
            updated.append({})
            for line in tag.LINES:
                var_list = []
                for var in line[4]:
                    if var[0] == 0:
                        var_list.append(self.VARIABLES.NAMESPACE_CALCULATED[var[1]])
                    else:
                        var_list.append(self.SharedInformation.MOD_VARIABLES[var[0]][var[1]])
                updated[-1][line[1]] = line[2].format(*var_list)

        for indx in xrange(len(self.TAGS)):
            tag = self.TAGS[indx]
            updated_tag = tag.condition_update(updated, self.TAG_NAMES)

        return updated


#############################################################

# interprets widgets and render for display driver
class WidgetInterpreter():
    PIXEL_BUFFER = []
    PIXEL_BUFFER1 = []

    def __init__(self, SharedInformation):
        self.SharedInformation = SharedInformation
        self.width = self.SharedInformation.width
        self.height = self.SharedInformation.height

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

        return deepcopy(self.PIXEL_BUFFER)

    def gfx_mgr(self, tag):
        if "type" in tag:

            type = tag["type"]
            if type == "none":
                self.gfx_none()
            elif type == "line":
                self.gfx_line(tag)
            elif type == "point":
                self.gfx_point(tag)
            elif type == "text":
                self.gfx_text(tag)
            elif type == "rect":
                self.gfx_rect(tag)
            elif type == "source":
                self.gfx_src(tag)
            elif type == "scrolled_text":
                self.gfx_scrolled_text(tag)

    def gfx_none(self):
        pass

    def set_options(self, options, tag):
        for t in tag.keys():
            # insert here special options like text is a string, colour a list etc
            if t == "colour":
                col = tag[t].split(",")
                options[t] == [int(col[0]), int(col[1]), int(col[2])]
            elif t == "text":
                options[t] = tag[t]

            else:

                try:
                    options[t] = int(tag[t])
                except ValueError:
                    options[t] = tag[t]
                except KeyError:
                    pass
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
        options = {"startx": 0, "starty": 0, "source":0, "colour":[1, 1, 1]}
        options = self.set_options(self.options, tag)
        startx = options["startx"]
        starty = options["starty"]
        source = options["source"]
        colour = options["colour"]

        self._tag = tag
        self.options = {"startx": 0, "starty": 0, "colour": [1, 1, 1], "text": "", "font_name": "default5x3", }
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

        if source != 0:
            if source[0] == "*":
                px_data = self.SOURCES.get_widget_source(source[1:], self.widget_name)
            else:
                px_data = self.SOURCES.get_source(source)
            try:
                for y in xrange(len(px_data)):
                    for x in xrange(len(px_data[y])):
                        xx = startx + x
                        yy = starty + y
                        if px_data[y][x] == 1:
                            self.PIXEL_BUFFER[xx][yy] = colour

            except:
                self.ERROR = self.ERROR + 1

    def gfx_scrolled_text(self, tag):
        options = {"startx": 0, "starty": 0, "text": 0, "colour" : [1, 1, 1], "overscan" : 0, "endx" : 9999,  "text": "", "font_name": "default5x3", "direction" : 1}
        options = self.set_options(options, tag)
        startx = options["startx"]
        starty = options["starty"]
        endx = options["endx"]
        colour = options["colour"]
        text = options["text"]
        overscan = options["overscan"]
        font_name = options["font_name"]
        direction = options["direction"]
        try:
            x = startx
            y = starty
            c = 0
            text_length = 0
            for i in xrange(len(text)):
                char = text[i]
                px_data = self.FONTS.get_char_from_font(font_name, char)
                text_length = text_length + len(px_data[0]) + 1

            text_length = text_length - 1
            overscan = (overscan % text_length) * direction
            for i in xrange(len(text)):

                char = text[i]
                if char == " ":
                    char = "SPACE"
                px_data = self.FONTS.get_char_from_font(font_name, char)
                y = starty

                if x - overscan < len(self.PIXEL_BUFFER):
                    for ii in xrange(len(px_data)):
                        x = startx + c
                        for iii in xrange(len(px_data[0])):
                            real_x = x - overscan
                            if px_data[ii][iii] != "0" and real_x < self.width and y < self.height and real_x < endx and real_x >= startx:

                                WidgetInterpreter.PIXEL_BUFFER[real_x][y] = colour
                            x = x + 1
                        y = y + 1
                    c = c + len(px_data[0]) + 1
                else:
                    pass
        except IOError:
            self.ERROR = self.ERROR + 1


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

def seperate_line(string, str="="):
    line = string.split(str)
    att = line[0]
    string = ""

    for c in line[1:]:
        string = string + c + str
    string = string[:-len(str)]
    data = [att, string]#
    return data

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

def find_strings(string, to_find):
    return [i for i in range(len(string)) if string.startswith(to_find, i)]

def compare(arg1, arg2, cmp):

    if type(cmp) == list:
        c_count = 0
        for c in xrange(len(cmp)-1):

            if cmp[c] == True:
                c_count = c_count + 1

        if arg1 == "AND":

            if c_count == len(cmp)-1:
                return True
            else:
                return False
        elif arg1 == "OR":
            if c_count > 0:
                return True
            else:
                return False
        else:
            return False
    elif cmp == "==" or cmp == "!=":
        arg1 = str(arg1)
        arg2 = str(arg2)
        if cmp == "==":
            if arg1 == arg2:
                return True
            else:
                return False
        elif cmp == "!=":
            if arg1 != arg2:
                return True
            else:
                return False
        else:
            return False
    elif cmp == "<" or cmp == ">" or cmp == "<=" or cmp == ">=":
        try:
            arg1 = float(arg1)
            arg2 = float(arg2)

            if cmp == "<":
                if arg1 < arg2:
                    return True
                else:
                    return False
            elif cmp == ">":
                if arg1 > arg2:
                    return True
                else:
                    return False
            elif cmp == "<=":
                if arg1 <= arg2:
                    return True
                else:
                    return False
            elif cmp == ">=":
                if arg1 >= arg2:
                    return True
                else:
                    return False
            else:
                return False

        except:
            return False
    else:
        return False

def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z




