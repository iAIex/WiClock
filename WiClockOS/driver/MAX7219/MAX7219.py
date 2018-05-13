import spidev
import time
from copy import deepcopy


# This display driver is inspired by the multilineMAX7219 driver library from
# website: https://tutorials-raspberrypi.de/bibliothek-fuer-mehrzeilige-m-x-n-max7219-led-matrizen/
# git-hub: https://github.com/tutRPi/multilineMAX7219.git
# Many thanks for the inspiration and part of the library!
class driver():
    NO_OP = [0, 0]
    REG_NOOP = 0x0
    REG_DIGIT0 = 0x1
    REG_DIGIT1 = 0x2
    REG_DIGIT2 = 0x3
    REG_DIGIT3 = 0x4
    REG_DIGIT4 = 0x5
    REG_DIGIT5 = 0x6
    REG_DIGIT6 = 0x7
    REG_DIGIT7 = 0x8
    REG_DECODEMODE = 0x9
    REG_INTENSITY = 0xA
    REG_SCANLIMIT = 0xB
    REG_SHUTDOWN = 0xC
    REG_DISPLAYTEST = 0xF

    def __init__(self, WidgetMgr, width, height):
        self.WidgetMgr = WidgetMgr
        self.width = width
        self.height = height
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 976000
        self.NUM_MATRICES = self.width / 8

        self.send_all_reg_byte(self.REG_SCANLIMIT, 7)  # show all 8 digits
        self.send_all_reg_byte(self.REG_DECODEMODE, 0)  # using a LED matrix (not digits)
        self.send_all_reg_byte(self.REG_DISPLAYTEST, 0)  # no display test
        self.send_all_reg_byte(self.REG_SHUTDOWN, 1)
        self.Brightness = self.WidgetMgr.DISPLAY_INFOS[2]

        print ">> Serial Interface loaded!"

        self.set_all()
        time.sleep(1)
        self.brightness(self.Brightness)
        self.PIXEL_BUFFER = [[[0, 0, 0] for x in xrange(self.width)] for x1 in xrange(self.height)]
        self.PIXEL_BUFFER_DIPLAYED = [[[0, 0, 0] for x in xrange(self.width)] for x1 in xrange(self.height)]

    def send_reg_byte(self, register, data):
        # Send one byte of data to one register via SPI port, then raise CS to latch
        # Note that subsequent sends will cycle this tuple through to successive MAX7219 chips
        self.spi.xfer([register, data])

    def send_bytes(self, datalist):
        # Send sequence of bytes (should be [register,data] tuples) via SPI port, then raise CS
        # Included for ease of remembering the syntax rather than the native spidev command, but also to avoid reassigning to 'datalist' argument
        self.spi.xfer2(datalist[:])

    def send_all_reg_byte(self, register, data):
        # Send the same byte of data to the same register in all of the MAX7219 chips
        self.send_bytes([register, data] * self.NUM_MATRICES)

    def clear_all(self):
        # Clear all of the connected MAX7219 matrices
        for self.col in range(8):
            self.send_all_reg_byte(self.col + 1, 0)

    def set_all(self):
        # Clear all of the connected MAX7219 matrices
        for self.col in range(8):
            self.send_all_reg_byte(self.col + 1, 0x0)

    def brightness(self, intensity):
        # Set a specified brightness level on all of the connected MAX7219 matrices
        # Intensity: 0-15 with 0=dimmest, 15=brightest; in practice the full range does not represent a large difference
        self.intensity = int(max(0, min(15, intensity)))
        self.send_bytes([self.REG_INTENSITY, intensity] * self.NUM_MATRICES)

    def send_matrix_reg_byte(self, matrix, register, data):
        # Send one byte of data to one register in just one MAX7219 without affecting others
        # padded_data = self.REG_NOOP * (self.NUM_MATRICES - 1 - matrix) + [register, data] + self.REG_NOOP * matrix
        padded_data = self.NO_OP * matrix + [register, data] + self.NO_OP * (self.NUM_MATRICES - 1 - matrix)
        self.send_bytes(padded_data)

    ##########################################################################

    def draw(self):
        # print 111

        if self.PIXEL_BUFFER_DIPLAYED != self.PIXEL_BUFFER:
            # self.clear_all()
            for self.matrix in xrange(self.NUM_MATRICES):
                # print ">> MAtrix Nummer: ", self.matrix
                for self.y in xrange(0, 8):
                    self.data = 0
                    self.pot = 7
                    for self.x in xrange(0, 8):
                        self.x = self.matrix * 8 + self.x
                        self.px = self.PIXEL_BUFFER[self.x][self.y]
                        if self.px[0] != 0 or self.px[1] != 0 or self.px[2] != 0:
                            self.data = self.data + 1 * 2 ** self.pot
                        self.pot = self.pot - 1
                        # print self.data

                    self.send_matrix_reg_byte(self.matrix, self.y + 1, self.data)
            self.PIXEL_BUFFER_DIPLAYED = deepcopy(self.PIXEL_BUFFER)


    def exit(self):
        self.clear_all()

    def set(self, BUFFER):
        self.PIXEL_BUFFER = deepcopy(BUFFER)
