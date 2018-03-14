import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
from current_work.utils.ImageProcessor import norm_image


class CoronalPlaneGUI(tk.Toplevel):
    def __init__(self, ct_arrs: np.ndarray, pt_arrs: np.ndarray, patient_info: dict):
        super().__init__()
        # 窗口设置
        self._window_size = (1000, 1024)  # height, width
        self.top_level = self
        self.top_level.title("Coronal Plane View")
        self.top_level.geometry("1024x1000+0+0")
        self.top_level.bind("<Key-Left>", self.prev_page_callback)
        self.top_level.bind("<Key-Right>", self.next_page_callback)
        self.top_level.protocol("WM_DELETE_WINDOW", self.close_window_callback)
        self.top_level.focus_set()

        # 数据设置
        self.current_index = 0
        self.total_img_num = -1
        self.patient_info = patient_info
        self.ct_arrs = self.from_transverse_plane_to_coronal_plane(ct_arrs)
        self.pt_arrs = self.from_transverse_plane_to_coronal_plane(pt_arrs)

        # UI设置

        # ct frame
        ct_frame = tk.Frame(self.top_level)
        ct_frame.grid(row=0, column=0)
        self.ct_canvas = tk.Canvas(ct_frame, width=512, height=1000)
        self.ct_canvas.pack()

        # pt frame
        pt_frame = tk.Frame(self.top_level)
        pt_frame.grid(row=0, column=1)
        self.pt_canvas = tk.Canvas(pt_frame, width=512, height=1000)
        self.pt_canvas.pack()

        # right most frame
        right_frame = tk.Frame(self.top_level)
        right_frame.grid(row=0, column=1)

    def load_images(self):
        # 加载ct
        ct_arr = norm_image(self.ct_arrs[self.current_index])
        self.current_ct_img = ImageTk.PhotoImage(self.resize_to_fit_screen(ct_arr))
        self.ct_canvas.create_image(0, 0, image=self.current_ct_img, anchor=tk.NW)

        pt_arr = norm_image(self.pt_arrs[self.current_index])
        self.current_pt_img = ImageTk.PhotoImage(self.resize_to_fit_screen(pt_arr))
        self.pt_canvas.create_image(0, 0, image=self.current_pt_img, anchor=tk.NW)

        # 设置title
        self.top_level.title("Coronal Plane View ({} / {})".format(self.current_index + 1, self.total_img_num))

    def from_transverse_plane_to_coronal_plane(self, ct_arrs):
        """从横断面转到冠状面"""
        ct_arrs = ct_arrs.transpose([1, 0, 2])
        self.total_img_num = len(ct_arrs)
        # 将图像拉伸
        _ratio = self.patient_info['pixelSpacing'][1] / self.patient_info['sliceThickness']
        _old_size = ct_arrs[0].shape
        print("[INFO] original image size: {}".format(_old_size))
        _new_size = (_old_size[0] / _ratio, _old_size[1])
        print("[INFO] new image size: {}".format(_new_size))
        print("[INFO] view limit: {}".format(self._window_size))
        _fit_ratio = min(self._window_size[0] / _new_size[0], self._window_size[1] / _new_size[1])
        print("[INFO] view size: {}".format([int(_new_size[0] * _fit_ratio), int(_new_size[1] * _fit_ratio)]))
        _ct_arr_list = list()
        for i in range(ct_arrs.shape[0]):
            _img = Image.fromarray(ct_arrs[i]).resize([int(_new_size[1]), int(_new_size[0])])
            _arr = np.array(_img)
            del _img
            _ct_arr_list.append(_arr)
        return np.stack(_ct_arr_list, axis=0)

    def resize_to_fit_screen(self, arr: np.ndarray):
        """根据窗口大小缩放图像"""
        _fit_ratio = min(self._window_size[0] / arr.shape[0], self._window_size[1] / arr.shape[1])
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

    def close_window_callback(self):
        """
        关闭子窗口时，绑定在子类实例上的数组所占内存并没有被释放，容易导致内存溢出
        因此自定义关闭窗口回调函数，删除其所占内存
        """
        del self.ct_arrs
        del self.pt_arrs
        self.top_level.destroy()
