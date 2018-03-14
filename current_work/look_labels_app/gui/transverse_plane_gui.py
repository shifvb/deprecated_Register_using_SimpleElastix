import time
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
from current_work.utils.ImageProcessor import norm_image, threshold_image
from current_work.utils import Clock


class TransversePlaneGUI(tk.Toplevel):
    def __init__(self, ct_arrs, suv_arrs, mask_arrs):
        super().__init__()
        self.top_level = self
        self.top_level.title("Transverse Plane View")
        self.top_level.geometry("1920x1080")
        self.top_level.bind("<Left>", self.prev_image_callback)
        self.top_level.bind("<Right>", self.next_image_callback)
        self.top_level.focus_set()

        self.ct_arrs = ct_arrs
        self.suv_arrs = suv_arrs
        self.mask_arrs = mask_arrs
        self.current_index = -1  # 当前图片索引
        self.total_img_num = -1  # 共有多少组图片
        self.clock = Clock(0.09)

        # ct frame
        self.ct_frame = tk.Frame(self.top_level, width=512, height=512)
        self.ct_frame.propagate(False)
        self.ct_frame.grid(row=0, column=0)
        self.ct_canvas = tk.Canvas(self.ct_frame, width=512, height=512)
        self.ct_canvas.pack()

        # ct & label frame
        self.ctl_frame = tk.Frame(self.top_level, width=512, height=512)
        self.ctl_frame.propagate(False)
        self.ctl_frame.grid(row=1, column=0)
        self.ctl_canvas = tk.Canvas(self.ctl_frame, width=512, height=512)
        self.ctl_canvas.pack()

        # suv frame
        self.suv_frame = tk.Frame(self.top_level, width=512, height=512)
        self.suv_frame.propagate(False)
        self.suv_frame.grid(row=0, column=1)
        self.suv_canvas = tk.Canvas(self.suv_frame, width=512, height=512)
        self.suv_canvas.pack()

        # suv & label frame
        self.suvl_frame = tk.Frame(self.top_level, width=512, height=512)
        self.suvl_frame.propagate(False)
        self.suvl_frame.grid(row=1, column=1)
        self.suvl_canvas = tk.Canvas(self.suvl_frame, width=512, height=512)
        self.suvl_canvas.pack()

        # label frame
        self.label_frame = tk.Frame(self.top_level, width=512, height=512)
        self.label_frame.propagate(False)
        self.label_frame.grid(row=1, column=2)
        self.label_canvas = tk.Canvas(self.label_frame, width=512, height=512)
        self.label_canvas.pack()

        right_frame = tk.LabelFrame(self.top_level, text="suv threshold")
        right_frame.grid(row=0, column=3)
        # 调整SUV阈值
        self.suv_threshold_frame = tk.LabelFrame(right_frame, width=384, text="SUV阈值")
        # self.suv_threshold_frame.propagate(False)
        self.suv_threshold_frame.grid(row=1, column=0)
        self.suv_scale = tk.Scale(self.suv_threshold_frame)
        self.suv_scale.configure(from_=1.0, to=2.5, resolution=0.1, orient=tk.HORIZONTAL,
                                 command=self.suv_scale_callback, length=380)
        self.suv_scale.set(1.5)
        self.suv_scale.pack()

        # 加载后设置变量
        self.total_img_num = len(self.ct_arrs)
        self.current_index = 0
        # 加载图像
        self._load_images()

    def prev_image_callback(self, event=None):
        """用户点击上一张按钮回调函数"""
        if self.clock.tick() is False:
            return
        if self.current_index <= 0:  # 越界return
            self.current_index = self.total_img_num
        self.current_index -= 1
        self._load_images()

    def next_image_callback(self, event=None):
        """用户点击下一张按钮回掉函数"""
        if self.clock.tick() is False:
            return
        if self.current_index >= self.total_img_num - 1:  # 越界return
            self.current_index = -1
        self.current_index += 1
        self._load_images()

    def _load_images(self):
        """加载界面图像"""
        # (row_0, col_0) 加载ct
        ct_arr = norm_image(self.ct_arrs[self.current_index])
        self.current_ct_img = ImageTk.PhotoImage(Image.fromarray(ct_arr, "L"))
        self.ct_canvas.create_image(0, 0, image=self.current_ct_img, anchor=tk.NW)
        self.ct_canvas.create_text(20, 20, text="CT", fill="yellow", font=("Arial", 20, "normal"), anchor=tk.NW)
        # (row_0, col_1)加载suv
        suv_arr = norm_image(self.suv_arrs[self.current_index])
        self.current_suv_img = ImageTk.PhotoImage(Image.fromarray(suv_arr, "L").resize([512, 512]))
        self.suv_canvas.create_image(0, 0, image=self.current_suv_img, anchor=tk.NW)
        self.suv_canvas.create_text(20, 20, text="SUV", fill="yellow", font=("Arial", 20, "normal"), anchor=tk.NW)

        # 加载mask
        mask_arr = norm_image(self.mask_arrs[self.current_index])

        # (row_1, col_0) 加载ct&label
        arr_0 = np.array(ct_arr)
        arr_1 = (np.array(mask_arr)[:, :, 0] > 128) * 255
        arr_2 = np.empty(shape=[3, arr_0.shape[0], arr_0.shape[1]], dtype=np.uint8)
        arr_2[0] = (arr_0 + arr_1) / 2  # R通道
        arr_2[1] = arr_0  # G通道
        arr_2[2] = arr_1  # B通道
        arr_2 = arr_2.transpose([1, 2, 0])
        self.current_ctl_img = ImageTk.PhotoImage(Image.fromarray(arr_2, "RGB"))
        self.ctl_canvas.create_image(0, 0, image=self.current_ctl_img, anchor=tk.NW)
        self.ctl_canvas.create_text(20, 20, text="CT & Label", fill="yellow", font=("Arial", 20, "normal"),
                                    anchor=tk.NW)
        # (row_1, col_1) 加载suv&label
        arr_0 = np.array(suv_arr)
        arr_1 = (np.array(mask_arr)[:, :, 0] > 128) * 255
        arr_2 = np.empty(shape=[3, arr_0.shape[0], arr_0.shape[1]], dtype=np.uint8)
        arr_2[0] = (arr_0 + arr_1) / 2  # R通道
        arr_2[1] = arr_0  # G通道
        arr_2[2] = arr_1  # B通道
        arr_2 = arr_2.transpose([1, 2, 0])
        self.current_suvl_img = ImageTk.PhotoImage(Image.fromarray(arr_2, "RGB"))
        self.suvl_canvas.create_image(0, 0, image=self.current_suvl_img, anchor=tk.NW)
        self.suvl_canvas.create_text(20, 20, text="SUV & Label", fill="yellow", font=("Arial", 20, "normal"),
                                     anchor=tk.NW)
        # (row_1, col_2) 加载suv > 1.5
        self.suv_scale_callback()

        # 设置title
        self.top_level.title("当前图像: {}/{}".format(self.current_index + 1, self.total_img_num))

    def suv_scale_callback(self, *args):
        thsuv_arr = threshold_image(self.suv_arrs[self.current_index], self.suv_scale.get()) * 255
        self.current_thsuv_img = ImageTk.PhotoImage(Image.fromarray(thsuv_arr, "L"))
        self.label_canvas.create_image(0, 0, image=self.current_thsuv_img, anchor=tk.NW)
        self.label_canvas.create_text(20, 20, fill="yellow", font=("Arial", 20, "normal"), anchor=tk.NW,
                                      text="SUV > {}".format(self.suv_scale.get()))
