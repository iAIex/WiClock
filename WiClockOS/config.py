import copy

def is_string(to_test):
    if to_test[0] == "\"":
        return str(to_test[1:-1])
    else:
        return int(to_test)


def read_cfg(path):
    data = {}
    l_count=0
    try:
        d = open(path, "r")
        lines = d.readlines()
        d.close()
    except:
        print ">> Path or file error"
        return 0
    try:

        for line in lines:
            if line[0] == "#" or line == "\n":
                pass
            else:
                line = line[0:-1]
                line = line.split("=")
                if line[1][0] == "[":
                    list = line[1][1:-1]
                    list = list.split(",")
                    list_new = []
                    for i in list:
                        list_new.append(is_string(i))
                    data[line[0]] = copy.deepcopy(list_new)


                else:
                    data[line[0]] = is_string(line[1])
            l_count = l_count + 1

        return data
    except IOError:
        print (">> error in line %d: " %l_count), line






