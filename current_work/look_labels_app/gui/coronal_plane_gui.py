import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
from current_work.utils.ImageProcessor import norm_image
from current_work.utils import Clock


class CoronalPlaneGUI(tk.Toplevel):
    def __init__(self, ct_arrs: np.ndarray, pt_arrs: np.ndarray, mask_arrs: np.ndarray, patient_info: dict):
        super().__init__()
        # 窗口设置
        self._window_size = (1000, 1024)  # height, width
        self.top_level = self
        self.top_level.title("CoronalPlaneView")
        self.top_level.geometry("1536x1000+0+0")
        self.top_level.bind("<Key-Left>", self.prev_page_callback)
        self.top_level.bind("<Key-Right>", self.next_page_callback)
        self.top_level.protocol("WM_DELETE_WINDOW", self.close_window_callback)
        self.top_level.focus_set()
        self.clock = Clock(0.1)

        # 数据设置
        self.current_index = 0
        self.total_img_num = ct_arrs.shape[1]
        self.patient_info = patient_info
        self.ct_arrs = self.from_transverse_plane_to_coronal_plane(ct_arrs)
        self.pt_arrs = self.from_transverse_plane_to_coronal_plane(pt_arrs)
        self.mask_arrs = self.from_transverse_plane_to_coronal_plane(mask_arrs[:, :, :, 0])

        self.ct_arrs = norm_image(self.ct_arrs)
        self.pt_arrs = self.pt_arrs
        self.mask_arrs = norm_image(self.mask_arrs)

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
        # mask frame
        mask_frame = tk.Frame(self.top_level)
        mask_frame.grid(row=0, column=2)
        self.mask_canvas = tk.Canvas(mask_frame, width=512, height=1000)
        self.mask_canvas.pack()

        # right most frame
        right_frame = tk.Frame(self.top_level)
        right_frame.grid(row=0, column=1)

        # call method to load image
        self.load_images()

    def load_images(self):
        """在界面上加载图像"""
        # load ct image
        ct_arr = self.ct_arrs[self.current_index]
        self.current_ct_img = ImageTk.PhotoImage(self.resize_to_fit_screen(ct_arr))
        self.ct_canvas.create_image(0, 0, image=self.current_ct_img, anchor=tk.NW)
        # load pt image
        pt_arr = norm_image(self.pt_arrs[self.current_index])
        self.current_pt_img = ImageTk.PhotoImage(self.resize_to_fit_screen(pt_arr))
        self.pt_canvas.create_image(0, 0, image=self.current_pt_img, anchor=tk.NW)
        # load mask image
        mask_arr = self.mask_arrs[self.current_index]
        self.current_mask_img = ImageTk.PhotoImage(self.resize_to_fit_screen(mask_arr))
        self.mask_canvas.create_image(0, 0, image=self.current_mask_img, anchor=tk.NW)

        # set title
        self.top_level.title("CoronalPlaneView ({} / {})".format(self.current_index + 1, self.total_img_num))

    def from_transverse_plane_to_coronal_plane(self, arrs):
        """从横断面转到冠状面进行数组转换，
        第一步是转秩变为冠状面，第二步是根据DICOM文件中实际像素间距，将图像拉伸"""
        # 转秩
        arrs = arrs.transpose([1, 0, 2])
        # 图像拉伸
        _ratio = self.patient_info['sliceThickness'] / self.patient_info['pixelSpacing'][1]
        _old_size = arrs[0].shape
        _new_size = [int(_) for _ in (_old_size[0] * _ratio, _old_size[1])]
        _new_size.reverse()  # PIL.Image.resize() receive format of (width, height), rather than (height, width)
        return np.stack([np.array(Image.fromarray(_).resize(_new_size, Image.BILINEAR)) for _ in arrs], axis=0)

    def resize_to_fit_screen(self, arr: np.ndarray):
        """根据窗口大小缩放图像"""
        _fit_ratio = min(self._window_size[0] / arr.shape[0], self._window_size[1] / arr.shape[1])
        return Image.fromarray(arr).resize([int(arr.shape[1] * _fit_ratio), int(arr.shape[0] * _fit_ratio)],
                                           Image.BILINEAR)

    def prev_page_callback(self, *args):
        """上一张图像回调函数"""
        if self.clock.tick() is False:
            return
        if self.current_index <= 0:
            self.current_index = self.total_img_num - 1
        else:
            self.current_index -= 1
        self.load_images()

    def next_page_callback(self, *args):
        """下一张图像回调函数"""
        if self.clock.tick() is False:
            return
        if self.current_index >= self.total_img_num - 1:
            self.current_index = 0
        else:
            self.current_index += 1
        self.load_images()

    def close_window_callback(self):
        """关闭子窗口时，绑定在子类实例上的数组所占内存并没有被释放，容易导致内存溢出。
        因此自定义关闭窗口回调函数，删除其所占内存"""
        del self.ct_arrs
        del self.pt_arrs
        self.top_level.destroy()
