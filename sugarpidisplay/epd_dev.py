from tkinter import *
from PIL import Image, ImageTk


# Display resolution
EPD_WIDTH       = 122
EPD_HEIGHT      = 250

class EPD_Dev:
    def __init__(self):
        print("__init__")
        # root=Tk()

        # root.title("Epaper Mock")

        # w = Canvas(root, width=EPD_WIDTH, height=EPD_HEIGHT)
        # image = Image.new(
        #     '1', (EPD_HEIGHT, EPD_HEIGHT), 255)
        # w.create_image((25, 125), image=ImageTk.PhotoImage(image))

        # w.pack()

        # root.mainloop()
    FULL_UPDATE = 0

    def reset(self):
        pass

    def init(self, update):
        pass

    def getbuffer(self, image):
        return image

    def display(self, image):
        if image is not None:
            image.show()

    def Clear(self, color):
        pass

    def sleep(self):
        pass
