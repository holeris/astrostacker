import tkinter as tk
from astrostacker.gui.MainFrame import MainFrame


root = tk.Tk()
root.title('Obrabiarka kosmosu')
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)
app = MainFrame(root).grid(sticky='nwes')
root.mainloop()
