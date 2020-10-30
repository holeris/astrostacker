import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from astrostacker.img.scale import lingray
from astrostacker.img.debayer import debayer


# Frame for displaying images. Has 2 scrollbars.
class ImageView(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        # tkinter image
        self.canvas_image = None
        # PIL image
        self.image = None
        # zoom factor
        self.zoom_factor = 1.0

        # 2 rows and 2 columns
        # canvas for displaying image with 2 scrollbars
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)

        self.v_scrollbar = ttk.Scrollbar(self, orient='vertical')
        self.v_scrollbar.grid(row=0, column=1, sticky='nse')

        self.h_scrollbar = ttk.Scrollbar(self, orient='horizontal')
        self.h_scrollbar.grid(row=1, column=0, sticky='wse')

        self.canvas = tk.Canvas(self)
        self.canvas.bind("<MouseWheel>", self.__on_mouse_wheel)
        self.canvas_image = self.canvas.create_image(0, 0, anchor='nw', image=None)

        self.canvas.config(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)
        self.v_scrollbar.config(command=self.canvas.yview)
        self.h_scrollbar.config(command=self.canvas.xview)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        self.canvas.grid(row=0, column=0, sticky='nwse')
        self.canvas.image = None
        self.canvas.img = None

    # Draws PIL image in canvas.
    def __draw_image(self, image):
        img = ImageTk.PhotoImage(image=image)
        self.canvas.itemconfig(self.canvas_image, image=img)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        self.canvas.img = img

    # Displays data from 2D matrix as 8bit image.
    def show_image(self, data, debayer_data):
        scale = 255
        if debayer_data:
            data = debayer(data)
            data[:, :, 0] = lingray(data[:, :, 0], max=scale)
            data[:, :, 1] = lingray(data[:, :, 1], max=scale)
            data[:, :, 2] = lingray(data[:, :, 2], max=scale)
            data = data.astype(np.uint8)
            image = Image.fromarray(data, 'RGB')
        else:
            data = lingray(data, max=scale)
            data = data.astype(np.uint8)
            image = Image.fromarray(data)
        self.image = image
        self.canvas.update()
        new_width = self.image.width * self.zoom_factor
        image = self.__resize_image(image, new_width)
        self.__draw_image(image)

    # Resizes image.
    def __resize_image(self, image, width):
        if image is None:
            return image
        ratio = image.width / width
        height = int(image.height / ratio)
        width = int(width)
        image = image.resize((width, height))
        return image

    # Zooms image.
    def __zoom_image(self, factor):
        image = self.image
        image = self.__resize_image(image, image.width * factor)
        self.__draw_image(image)

    # Event zooming image in or out in reaction to mouse wheel movement.
    def __on_mouse_wheel(self, event):
        if self.image is None:
            return
        if event.delta > 0:
            new_zoom = self.zoom_factor + 0.1
        else:
            new_zoom = self.zoom_factor - 0.1
        if 0 < new_zoom <= 2:
            image = self.__resize_image(self.image, int(self.image.width * new_zoom))
            self.__draw_image(image)
            self.zoom_factor = new_zoom
