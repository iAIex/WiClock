import time
import datetime
class Module():
    def __init__(self, SharedInformation):
        self.SharedInformation = SharedInformation
        self.MODULE = {}

    def update(self):
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
        self.MODULE["UTC"] = str(time.time())
        return self.MODULE