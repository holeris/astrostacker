import logging
from threading import Thread
import numpy as np
import tkinter as tk
import tkinter.filedialog
from astrostacker.img.stack import stack
import tifffile as tf

logger = logging.getLogger()


# Frame with stacking control panel.
class StackingControlPanel(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        # list of files to be stacked
        self.filenames = None
        # index of reference frame
        self.ref_frame_idx = None

        # variable holding sate of debayer checkbox
        self.var_debayer = tk.IntVar()

        # 1 row and 2 columns
        # Debayer checkbox and stack button.
        self.cbDebayer = tk.Checkbutton(self, variable=self.var_debayer, text='Debayer stacked images')
        self.cbDebayer.grid(row=0, column=0, padx=5, pady=5)

        self.btnStack = tk.Button(self, text='Stack all images', command=self.cmd_stack)
        self.btnStack.grid(row=0, column=1, padx=5, pady=5)

    # Checks if filename already has tif or tiff extensions and adds tif extension if not.
    def __check_extension(self, filename):
        lower = filename.lower()
        if len(filename) < 3:
            extension_present = False
        elif lower.endswith('.tif') or lower.endswith('.tiff'):
            extension_present = True
        else:
            extension_present = False
        if not extension_present:
            filename = filename + '.tif'
        return filename

    # Sets new values of filenames and ref_frame_idx
    def set_filenames(self, filenames, ref_frame_idx):
        self.filenames = filenames
        self.ref_frame_idx = ref_frame_idx

    # Asks for filename and starts new thread for image stacking.
    def cmd_stack(self):
        debayer = self.var_debayer.get()
        files_to_stack = self.filenames
        ref_frame_idx = self.ref_frame_idx
        filename = tk.filedialog.asksaveasfilename(
            title='Select TIFF file for stacking result:',
            filetypes=(('TIFF files', '*.tif *.tiff'), ('all files', '*.*')))
        if filename == '':
            return
        filename = self.__check_extension(filename)

        thread = Thread(target=self.stack, args=(filename, files_to_stack, debayer, ref_frame_idx))
        thread.start()

    # Stacks images.
    def stack(self, filename, files_to_stack, debayer, ref_frame_idx):
        data = stack(files_to_stack, debayer, ref_frame_idx)
        if debayer:
            data = data.astype(np.uint16)
            r = data[:, :, 0]
            g = data[:, :, 1]
            b = data[:, :, 2]
            image = [r, g, b]
        else:
            image = data
        logger.info(f'Saving {filename:s}')
        tf.imwrite(filename, data)
        logger.info(f'{filename:s} saved.')
        logger.info('Stacking completed.')
