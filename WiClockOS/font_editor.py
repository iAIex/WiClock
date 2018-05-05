from Tkinter import *
def main():
    root = Tk()

    options(root)
    w = Label(root, text="Hello Tkinter!")

    w.pack()
    root.mainloop()


def options(root):
    options = Toplevel(root)
    options.attributes("-topmost", True)
    w = Label(options, text="Options")
    w.pack()
    w = Label(options, text="Height")
    w.pack()
    ey = Entry(options)
    ey.pack()
    w = Label(options, text="Width")
    w.pack()
    ex = Entry(options)
    ex.pack()
    w = Label(options, text="Name")
    en = Entry(options)
    w.pack()
    en.pack()


    x = 3
    y = 5
    name = "test"
    Button(options, text='OK', command=options_return(options, ex, ey, en)).grid(row=3, column=0, sticky=W, pady=4)

def options_return(options, ex, ey, en):

    options.quit()


main()