
import random
import threading
import copy
import pygame
import time


class driver(object):
    # PIXEL_BUFFER STORES RGB !
    PIXEL_BUFFER = []

    def __init__(self, WidgetMgr, width, height):
        self.WidgetMgr = WidgetMgr
        self.cfg_data = read_cfg("driver/simulator/config.cfg")
        self.px_x = width
        self.px_y = height
        self.px_size = self.cfg_data["px_size"]   # regulates the pixel size
        self.RGB = self.cfg_data["rgb"]        # turns RGB mode ON/OFF
        self.RECT = self.cfg_data["rect"]       # switch between rectengle or cyrcle
        self.PX_ON = self.cfg_data["px_on"]        # When RGB is off
        self.PX_OFF = self.cfg_data["px_off"]   # When RGB is off
        self.BG = self.cfg_data["bg"]
        self.overheat = self.cfg_data["overheat"]
        if self.RGB == 0:
            driver.PIXEL_BUFFER = [[self.PX_OFF for x in xrange(self.px_y)] for x1 in xrange(self.px_x)]
        else:
            driver.PIXEL_BUFFER = [[[0, 0, 0] for x in xrange(self.px_y)] for x1 in xrange(self.px_x)]


        print "--- - - - WiClockOS Simulator v. 1.0 - (C) Bastian Frey 2018 - - - ---"

        threading._start_new_thread(self._draw, ())

    def draw(self):
        pass

    def _draw(self):

        pygame.init()


        self._display_surf = pygame.display.set_mode(
            (self.px_x * self.px_size + self.overheat + 150, self.px_y * self.px_size + self.overheat + 300))
        # R, G, B

        pygame.display.set_caption("WiClockOS Simulator v. 1.0")
        self.clock = pygame.time.Clock()
        pygame.font.init()  # you have to call this at the start,
        # if you want to use this module.
        self.myfont = pygame.font.SysFont('Comic Sans MS', 30)
        self.running = True
        self.button_left = (20 , self.px_y * self.px_size + self.overheat + 20, 150, 50)
        self.button_home = (190, self.px_y * self.px_size + self.overheat + 20, 200, 50)
        self.button_right = (410, self.px_y * self.px_size + self.overheat + 20, 150, 50)
        self.buttons = [self.button_left, self.button_home, self.button_right]
        while self.running:
            self._display_surf.fill(self.BG)
            self.draw_buttons()
            # GPIO
            pygame.draw.rect(self._display_surf, (0,0,0),(self.px_x * self.px_size + self.overheat + 20, 0, 110, self.px_y * self.px_size + self.overheat))
            # Display loop
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
            # Event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:

                        pygame.event.post(pygame.event.Event(pygame.QUIT))
                    if event.key == pygame.K_RIGHT:
                        self.WidgetMgr.ACTION(["WIDGET", "RIGHT"])
                    if event.key == pygame.K_LEFT:
                        self.WidgetMgr.ACTION(["WIDGET", "LEFT"])
                    if event.key == pygame.K_SPACE:
                        self.WidgetMgr.ACTION(["WIDGET", "HOME"])
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.button()



            pygame.display.flip()

            self.clock.tick(0)
        print ">> Simulator Closed! Program still running!"

    def draw_buttons(self):
        # Buttons
        pygame.draw.rect(self._display_surf, (0, 0, 0), self.button_left)
        textsurface = self.myfont.render("<- LEFT", False, (255, 255, 255))
        self._display_surf.blit(textsurface, (40, self.px_y * self.px_size + self.overheat + 25))
        pygame.draw.rect(self._display_surf, (0, 0, 0), self.button_home)
        textsurface = self.myfont.render("< HOME >", False, (255, 255, 255))
        self._display_surf.blit(textsurface, (210, self.px_y * self.px_size + self.overheat + 25))
        pygame.draw.rect(self._display_surf, (0, 0, 0), self.button_right)
        textsurface = self.myfont.render("RIGHT ->", False, (255, 255, 255))
        self._display_surf.blit(textsurface, (420, self.px_y * self.px_size + self.overheat + 25))

    def set(self, pixel_data):
        driver.PIXEL_BUFFER = copy.deepcopy(pixel_data)

    def exit(self):
        pass

    def get_data(self):
        return [self.px_x, self.px_y, self.RGB, driver.PIXEL_BUFFER]

    def button(self):
        #print pygame.mouse.get_pos()
        self.mxy = pygame.mouse.get_pos()
        for self.i in xrange(len(self.buttons)):
            if self.mxy[0] > self.buttons[self.i][0] and self.mxy[1] > self.buttons[self.i][1] and \
                self.mxy[0] < self.buttons[self.i][2] + self.buttons[self.i][0] and \
                self.mxy[1] < self.buttons[self.i][3] + self.buttons[self.i][1]:
                self.id = 0
                if self.i == 1:
                    self.id = "HOME"
                elif self.i == 0:
                    self.id = "LEFT"
                elif self.i == 2:
                    self.id = "RIGHT"
                self.WidgetMgr.ACTION(["WIDGET", self.id])

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
