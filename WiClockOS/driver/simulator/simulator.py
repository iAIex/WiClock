import pygame
import random
import threading
import copy
import time
class driver(object):
    # PIXEL_BUFFER STORES RGB !
    PIXEL_BUFFER = []

    def __init__(self):
        self.cfg_data = read_cfg("driver/simulator/config.cfg")
        #self.cfg_data = read_cfg("config.cfg")
        self.px_x = self.cfg_data["width"]
        self.px_y = self.cfg_data["height"]
        self.px_size = self.cfg_data["px_size"]   # regulates the pixel size
        self.RGB = self.cfg_data["rgb"]        # turns RGB mode ON/OFF
        self.RECT = self.cfg_data["rect"]       # switch between rectengle or cyrcle
        self.PX_ON = self.cfg_data["px_on"]        # When RGB is off
        self.PX_OFF = self.cfg_data["px_off"]   # When RGB is off
        self.BG = self.cfg_data["bg"]
        self.overheat = self.cfg_data["overheat"]


        pygame.init()
        self.px_x = self.px_x
        self.px_y = self.px_y

        self._display_surf = pygame.display.set_mode((self.px_x * self.px_size + self.overheat, self.px_y * self.px_size + self.overheat))
                                #R, G, B
        pygame.display.set_caption("WiClockOS Simulator v. 1.0")
        if self.RGB == 0:
            driver.PIXEL_BUFFER = [[self.PX_OFF for x in xrange(self.px_y)] for x1 in xrange(self.px_x)]
        else:
            driver.PIXEL_BUFFER = [[[0, 0, 0] for x in xrange(self.px_y)] for x1 in xrange(self.px_x)]
        self._display_surf.fill(self.BG)

        print "--- - - - WiClockOS Simulator v. 1.0 - (C) Bastian Frey 2018 - - - ---"
        threading._start_new_thread(self._draw, ())

    def draw(self):
        pass
    def _draw(self):
        self.clock = pygame.time.Clock()
        self.running = True
        while self.running:
            for self.x in xrange(self.px_x):
                for self.y in xrange(self.px_y):
                    self.px_data = driver.PIXEL_BUFFER[self.x][self.y]
                    if self.RECT == 0:
                        if self.RGB == 0:

                            if (self.px_data[0] != 0) or (self.px_data[1] != 0) or(self.px_data[2] != 0):
                                self.px_data = self.PX_ON
                            else:
                                self.px_data = self.PX_OFF

                        pygame.draw.circle(self._display_surf, self.px_data,
                                           (int(self.x * self.px_size + 0.5 * self.px_size), int(self.y * self.px_size + 0.5 * self.px_size)),
                                           self.px_size/2 - self.overheat)



                    else:
                        if self.RGB == 0:
                            if (self.px_data[0] != 0) or (self.px_data[1] != 0) or(self.px_data[2] != 0):
                                self.px_data = self.PX_ON
                            else:
                                self.px_data = self.PX_OFF

                        pygame.draw.rect(self._display_surf, self.px_data,
                                           (int(self.x * self.px_size + self.overheat),
                                            int(self.y * self.px_size + self.overheat),
                                            self.px_size - self.overheat, self.px_size - self.overheat),
                                           0)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:

                        pygame.event.post(pygame.event.Event(pygame.QUIT))
            pygame.display.flip()
            self.clock.tick(0)

    def set(self, pixel_data):
        driver.PIXEL_BUFFER = copy.deepcopy(pixel_data)
    def exit(self):
        pass

    def get_data(self):
        return [self.px_x, self.px_y, self.RGB, driver.PIXEL_BUFFER]


def is_string(to_test):
    if to_test[0] == "\"":
        return str(to_test[1:-1])
    else:
        return int(to_test)


def read_cfg(path):
    data = {}
    import copy
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
    except:
        print (">> error in line %d: " %l_count), line

def test():
    m = driver()
    data = m.get_data()

    while True:
        x = random.randint(0, data[0]-1)
        y = random.randint(0, data[1]-1)
        driver.PIXEL_BUFFER[x][y] = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
        m.draw()
