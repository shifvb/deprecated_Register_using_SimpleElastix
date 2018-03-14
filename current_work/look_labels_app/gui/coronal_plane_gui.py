import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
from current_work.utils.ImageProcessor import norm_image


class CoronalPlaneGUI(tk.Toplevel):
    def __init__(self, ct_arrs: np.ndarray, patient_info: dict):
        super().__init__()
        self.top_level = self
        self.top_level.title("Coronal Plane View")
        self.top_level.geometry("500x400+0+0")
        self.top_level.bind("<Key-Left>", self.prev_page_callback)
        self.top_level.bind("<Key-Right>", self.next_page_callback)
        self.top_level.focus_set()

        self.ct_arrs = np.array(ct_arrs.transpose([1, 0, 2]))
        self.current_index = 0
        self.total_img_num = len(self.ct_arrs)

        ct_frame = tk.Frame(self.top_level)
        ct_frame.grid(row=0, column=0)
        self.ct_canvas = tk.Canvas(ct_frame, width=512, height=512)
        self.ct_canvas.pack()

        # right most frame
        right_frame = tk.Frame(self.top_level)
        right_frame.grid(row=0, column=1)
        print(patient_info)

    def load_images(self):
        ct_arr = norm_image(self.ct_arrs[self.current_index])
        self.current_ct_img = ImageTk.PhotoImage(Image.fromarray(ct_arr))
        self.ct_canvas.create_image(0, 0, image=self.current_ct_img, anchor=tk.NW)

    def prev_page_callback(self, *args):
        if self.current_index <= 0:
            self.current_index = self.total_img_num - 1
        else:
            self.current_index -= 1
        self.load_images()

    def next_page_callback(self, *args):
        if self.current_index >= self.total_img_num - 1:
            self.current_index = 0
        else:
            self.current_index += 1
        self.load_images()
