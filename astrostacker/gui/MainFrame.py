import logging; logging.basicConfig(level=logging.NOTSET)
import queue
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from astropy.io import fits as pyfits
from astrostacker.gui.ImageList import ImageList
from astrostacker.gui.ImageView import ImageView
from astrostacker.gui.StackingControlPanel import StackingControlPanel
from astrostacker.logging.loghandler import LogHandler
from astrostacker.img.debayer import RGGB

logger = logging.getLogger()


class MainFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=100)

        self.imageList = ImageList(self)
        self.imageList.grid(row=0, column=0, sticky='nws')
        self.imageList.event_on_select = self.display_image

        self.stackingPanel = StackingControlPanel(self)
        self.stackingPanel.grid(row=1, column=0, sticky='ws')
        self.stackingPanel.bayer_mask = RGGB
        self.imageList.event_on_change_filenames = self.stackingPanel.set_filenames
        self.imageList.event_on_change_bayer_mask = self.stackingPanel.set_bayer_mask

        self.scrolledText = ScrolledText(self, width=50, height=10)
        self.scrolledText.grid(row=2, column=0, columnspan=2, sticky='wes')

        self.log_queue = queue.Queue()
        self.log_handler = LogHandler(self.log_queue)

        formatter = logging.Formatter('%(asctime)s: %(message)s')
        self.log_handler.setFormatter(formatter)
        logger.addHandler(self.log_handler)

        self.imageView = ImageView(self)
        self.imageView.grid(row=0, column=1, rowspan=2, sticky='nwse')

        self.after(100, self.poll_log_queue)

    # loads and displays selected image
    def display_image(self, filename, debayer=False, bayer_mask=RGGB):
        img = pyfits.open(filename)
        data = img[0].data
        self.imageView.show_image(data, debayer, bayer_mask)

    # displays log message
    def display_message(self, record):
        msg = self.log_handler.format(record)
        self.scrolledText.configure(state='normal')
        self.scrolledText.insert(tk.END, msg + '\n')
        self.scrolledText.configure(state='disabled')
        # Autoscroll to the bottom
        self.scrolledText.yview(tk.END)

    # displays queued messages every 100ms
    def poll_log_queue(self):
        while True:
            try:
                record = self.log_queue.get(block=False)
            except queue.Empty:
                break
            else:
                self.display_message(record)
        self.after(100, self.poll_log_queue)
