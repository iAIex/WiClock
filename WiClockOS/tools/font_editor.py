from Tkinter import *
class font_createor():
    def __init__(self):

        self.width = 5
        self.height = 5
        self.size = 50
        self.PIXEL_BUFFER = [[0 for x in xrange(self.width)] for x1 in xrange(self.height)]
        self.root = Tk()
        self.root.title("WiClock Font Editor v1.0")
        self.frame_l = Frame(self.root)
        self.frame_r = Frame(self.root)
        self.frame_l.pack(side=LEFT)
        self.frame_r.pack(side=RIGHT)
        self.canvas = Canvas(self.frame_l, width=self.width * self.size+1, height=self.height * self.size+1)
        self.canvas.bind("<Button-1>", self.draw)
        self.canvas.pack(side=LEFT)
        self.T = Text(self.frame_r, height=20, width=30)

        self.T.pack()
        B_create = Button(self.frame_r, text="Create", command=self.create)
        B_create.pack(side=BOTTOM)
        self.checkered()
        self.root.mainloop()

    def draw(self, event):

        self.x = event.x / self.size * self.size
        self.y = event.y / self.size * self.size
        self.xx = event.x / self.size
        self.yy = event.y / self.size

        if self.PIXEL_BUFFER[self.xx][self.yy] == 1:
            self.PIXEL_BUFFER[self.xx][self.yy] = 0
            self.canvas.create_rectangle(self.x, self.y, self.x + self.size, self.y + self.size, fill="WHITE")
        else:
            self.PIXEL_BUFFER[self.xx][self.yy] = 1
            self.canvas.create_rectangle(self.x, self.y, self.x + self.size, self.y + self.size, fill="RED")
        self.checkered()
    def checkered(self):
        # vertical lines at an interval of "line_distance" pixel

        for x in range(0, self.width*self.size, self.size):
            self.canvas.create_line(x, 0, x, self.height*self.size, fill="#476042")
        # horizontal lines at an interval of "line_distance" pixel
        for y in range(0, self.height*self.size, self.size):
            self.canvas.create_line(0, y, self.width*self.size, y, fill="#476042")

    def create(self):
        self.T.delete(1.0, "end")
        for self.i in xrange(len(self.PIXEL_BUFFER)):
            self.data = "("
            for self.ii in xrange(len(self.PIXEL_BUFFER[0])):
               self.data = self.data + str(self.PIXEL_BUFFER[self.ii][self.i]) + ","
            self.data = self.data[0:-1] + ")\n"

            self.T.insert("end", self.data)


font_createor()