import logging
import tkinter as tk
import tkinter.filedialog
from tkinter import ttk
import tkinter.font as tkfont
from astrostacker.img.debayer import RGGB, BGGR, GRBG, GBRG


logger = logging.getLogger()


# Frame for displaying list of images
class ImageList(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        # list of filenames
        self.filenames = []
        # variable holding sate of debayer checkbox
        self.var_debayer = tk.IntVar()
        # variable holding sate of reference frame checkbox
        self.var_ref_frame = tk.IntVar()
        # variable holding value of bayer mask
        self.var_bayer_mask = tk.StringVar()
        self.var_bayer_mask.set(RGGB)
        # index of reference frame
        self.ref_frame_idx = 0
        # Fonts for image list
        self.font_img = tkfont.Font(font=('TkDefaultFont', 8))
        self.font_img_bold = tkfont.Font(font=('TkDefaultFont', 8, 'bold'))
        # function to be called when image is selected
        # arg0: filename (string)
        # arg1: debayer flag (boolean)
        self.event_on_select = None
        self.event_on_change_filenames = None
        self.event_on_change_bayer_mask = None

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # 2 rows and 0 columns
        # row 0 with control panel (tk.Frame with further controls)
        # row 1 with image list (tk.Frame with further controls)
        self.control_panel = tk.Frame(self, parent, *args, **kwargs)
        self.control_panel.grid(row=0, column=0, sticky='nw')
        self.image_list = tk.Frame(self, parent, *args, **kwargs)
        self.image_list.grid(row=1, column=0, sticky='nws')

        # control panel
        # 2 rows and 4 columns
        # Label | button add images | label | button clear images | checkbox debayer
        # checkbox reference frame | label | option menu bayer mask
        ctrl = self.control_panel

        ctrl.lblSelectFitsImages = tk.Label(ctrl, text='Add FITS images:')
        ctrl.lblSelectFitsImages.grid(row=0, column=0, padx=5, pady=5)

        ctrl.btnSelectFiles = tk.Button(ctrl, text='+', command=self.__cmd_add_files)
        ctrl.btnSelectFiles.grid(row=0, column=1, padx=5, pady=5)

        ctrl.lblResetFitsImages = tk.Label(ctrl, text='Clear list:')
        ctrl.lblResetFitsImages.grid(row=0, column=2, padx=5, pady=5)

        ctrl.btnResetFiles = tk.Button(ctrl, text='Clear', command=self.__cmd_clear_files)
        ctrl.btnResetFiles.grid(row=0, column=3, padx=5, pady=5)

        ctrl.cbDebayer = tk.Checkbutton(ctrl, variable=self.var_debayer, text='Debayer displayed images')
        ctrl.cbDebayer.grid(row=0, column=4, padx=5, pady=5)

        ctrl.row1 = tk.Frame(ctrl)
        ctrl.row1.grid(row=1, column=0, columnspan=5, sticky='w')
        ctrl.cbRefFrame = tk.Checkbutton(ctrl.row1, variable=self.var_ref_frame,
                                         command=self.__on_cb_ref_frame_changed, text='Reference frame')
        ctrl.cbRefFrame.grid(row=0, column=0, padx=5, pady=5)

        ctrl.lblBayerMask = tk.Label(ctrl.row1, text='Bayer mask:')
        ctrl.lblBayerMask.grid(row=0, column=1, padx=5, pady=5)

        ctrl.omBayerMask = tk.OptionMenu(ctrl.row1, self.var_bayer_mask, RGGB, BGGR, GBRG, GRBG,
                                         command=self.__cmd_bayer_mask_changed)
        ctrl.omBayerMask.grid(row=0, column=2, padx=5, pady=5)

        # image list
        # 2 rows and 2 columns
        # treeview with 2 scrollbars
        lst = self.image_list
        lst.rowconfigure(0, weight=1)
        lst.columnconfigure(0, weight=1)
        lst.columnconfigure(1, weight=1)
        cols = ['Filename']
        lst.scrollbar_v = ttk.Scrollbar(lst, orient='vertical')
        lst.scrollbar_h = ttk.Scrollbar(lst, orient='horizontal')
        lst.treeview = ttk.Treeview(lst, columns=cols, show='headings',
                                    xscrollcommand=lst.scrollbar_h.set,
                                    yscrollcommand=lst.scrollbar_v.set)
        lst.treeview.bind('<<TreeviewSelect>>', self.__on_select)
        lst.treeview.bind("<Key>", self.__on_key_pressed)
        lst.treeview.tag_configure('NORMAL_TAG', font=self.font_img)
        lst.treeview.tag_configure('REF_TAG', font=self.font_img_bold)
        lst.scrollbar_h.config(command=lst.treeview.xview)
        lst.scrollbar_v.config(command=lst.treeview.yview)
        for col in cols:
            lst.treeview.heading(col, text=col)
            lst.treeview.column(col, width=400, stretch=True)
        lst.treeview.grid(row=0, column=0, sticky='nws')
        lst.scrollbar_v.grid(row=0, column=1, sticky='nws')
        lst.scrollbar_h.grid(row=1, column=0, sticky='wes')

    # Clears image list and puts all files from filenames in it.
    def __refresh_treeview(self, filenames):
        lst = self.image_list.treeview
        lst.delete(*lst.get_children())
        for i in range(0, len(filenames)):
            file = filenames[i]
            if i == self.ref_frame_idx:
                tag = 'REF_TAG'
            else:
                tag = 'NORMAL_TAG'
            self.image_list.treeview.insert('', 'end', values=[file, i], tag=tag)

    # Asks user to choose files and adds them to at the end of image list and self.filenames.
    def __cmd_add_files(self):
        new_filenames = tk.filedialog.askopenfilenames(
            title='Select files:',
            filetypes=(('fits files', '*.fit *.fits'), ('all files', '*.*')))
        if len(self.filenames) == 0:
            self.ref_frame_idx = 0
        for i in range(0, len(new_filenames)):
            file = new_filenames[i]
            if i + len(self.filenames) == self.ref_frame_idx:
                self.image_list.treeview.insert('', 'end', values=[file, i + len(self.filenames)], tag='REF_TAG')
            else:
                self.image_list.treeview.insert('', 'end', values=[file, i + len(self.filenames)], tag='NORMAL_TAG')
        self.filenames.extend(new_filenames)
        logger.info(f'{len(new_filenames):d} files added.')
        self.event_on_change_filenames(self.filenames, self.ref_frame_idx)

    # Clears image list.
    def __cmd_clear_files(self):
        self.filenames = []
        lst = self.image_list.treeview
        lst.delete(*lst.get_children())
        self.event_on_change_filenames(self.filenames, self.ref_frame_idx)

    # Event deleting selected row in react to press of delete key.
    def __on_key_pressed(self, event):
        if event.keysym == 'Delete':
            selected_items = self.image_list.treeview.selection()
            for i in range(0, len(selected_items)):
                selected_item = selected_items[i]
                item = self.image_list.treeview.item(selected_item)
                self.filenames.remove(item['values'][0])
                if i == self.ref_frame_idx:
                    self.ref_frame_idx = 0
            if len(selected_items) > 0:
                self.__refresh_treeview(self.filenames)
                self.event_on_change_filenames(self.filenames, self.ref_frame_idx)

    # Event displaying selected image.
    def __on_select(self, event):
        sel = self.image_list.treeview.item(event.widget.selection()[0])
        idx = sel['values'][1]
        if idx == self.ref_frame_idx:
            self.var_ref_frame.set(True)
            self.control_panel.cbRefFrame['state'] = 'disable'
        else:
            self.var_ref_frame.set(False)
            self.control_panel.cbRefFrame['state'] = 'normal'
        filename = self.filenames[idx]
        debayer = self.var_debayer.get()
        self.event_on_select(filename, debayer, self.var_bayer_mask.get())

    # Event setting new reference frame when checkbox is changed
    def __on_cb_ref_frame_changed(self):
        if len(self.image_list.treeview.selection()) == 0:
            return
        for idx in self.image_list.treeview.get_children():
            if self.image_list.treeview.item(idx)['values'][1] == self.ref_frame_idx:
                idx_old = idx
        idx_new = self.image_list.treeview.selection()[0]
        self.image_list.treeview.item(idx_old, tag='NORMAL_TAG')
        self.image_list.treeview.item(idx_new, tag='REF_TAG')
        item_new = self.image_list.treeview.item(idx_new)
        self.ref_frame_idx = item_new['values'][1]

    # Event setting new reference frame when checkbox is changed
    def __cmd_bayer_mask_changed(self, event):
        self.event_on_change_bayer_mask(self.var_bayer_mask.get())
