import platform
import time
from copy import deepcopy
from threading import _start_new_thread


class Addon():
    GPIOS = {4: [0, 0], 14: [0, 0], 15: [0, 0], 18: [0, 0]}
    DO = []
    BUTTON_PRESSED = []
    BUTTONS = {}
    def __init__(self, SharedInformation):
        self.SharedInformtaion = SharedInformation



    # GPIO THREAD FOR HANDLING

    def run(self):
        if platform.system() == "Linux":
            import RPi.GPIO as GPIO
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)

            for but in self.SharedInformtaion.BINDED_GPIOS:
                GPIO.setup(but, GPIO.IN)

        print ">> GPIO-Listener started !"
        buttons = self.SharedInformtaion.BINDED_GPIOS
        while platform.system() == "Linux":
            for but in buttons.keys():
                if GPIO.input(but) == GPIO.HIGH:
                    self.SharedInformtaion.threading_queue["ActionMgr"].put(["DisplayDriver", self.SharedInformtaion.BINDED_GPIOS[but]])
                    while GPIO.input(but) == GPIO.HIGH:
                        pass
            time.sleep(0.1)

        while True:
            self.SharedInformtaion.DEBUG_STRINGS["gpio"] = Addon.GPIOS
            time.sleep(1)
