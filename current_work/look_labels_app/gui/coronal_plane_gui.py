import tkinter as tk


class MyTopLevel(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.top_level = self
        self.top_level.title("Coronal Plane View")
        self.top_level.geometry("500x400+0+0")
        tk.Label(self.top_level, text="sdfs").grid(row=0, column=0)
