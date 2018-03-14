import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
from current_work.utils.ImageProcessor import norm_image


class CoronalPlaneGUI(tk.Toplevel):
    def __init__(self, ct_arrs: np.ndarray, patient_info: dict):
        super().__init__()
        self._window_size = (900, 1200)  # height, width
        self.top_level = self
        self.top_level.title("Coronal Plane View")
        self.top_level.geometry("{}x{}+0+0".format(*self._window_size))
        self.top_level.bind("<Key-Left>", self.prev_page_callback)
        self.top_level.bind("<Key-Right>", self.next_page_callback)
        self.top_level.focus_set()

        ct_arrs = ct_arrs.transpose([1, 0, 2])
        # 将图像拉伸
        _ratio = patient_info['pixelSpacing'][1] / patient_info['sliceThickness']
        _old_size = ct_arrs[0].shape
        _new_size = (_old_size[0] / _ratio, _old_size[1])
        _ct_arr_list = list()
        for i in range(ct_arrs.shape[0]):
            _img = Image.fromarray(ct_arrs[i]).resize([int(_new_size[1]), int(_new_size[0])])
            _arr = np.array(_img)
            _ct_arr_list.append(_arr)
        self.ct_arrs = np.stack(_ct_arr_list, axis=0)

        self.current_index = 0
        self.total_img_num = len(ct_arrs)

        ct_frame = tk.Frame(self.top_level)
        ct_frame.grid(row=0, column=0)
        self.ct_canvas = tk.Canvas(ct_frame, width=self._window_size[0], height=self._window_size[1])
        self.ct_canvas.pack()

        # right most frame
        right_frame = tk.Frame(self.top_level)
        right_frame.grid(row=0, column=1)

    def load_images(self):
        # 加载ct
        ct_arr = norm_image(self.ct_arrs[self.current_index])
        self.current_ct_img = ImageTk.PhotoImage(self.resize_to_fit_screen(ct_arr))
        self.ct_canvas.create_image(0, 0, image=self.current_ct_img, anchor=tk.NW)

        # 设置title
        self.top_level.title("{} / {}".format(self.current_index + 1, self.total_img_num))

    def resize_to_fit_screen(self, arr: np.ndarray):
        _fit_ratio = self._window_size[0] / arr.shape[0]
        return Image.fromarray(arr).resize([int(arr.shape[1] * _fit_ratio), int(arr.shape[0] * _fit_ratio)])

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
