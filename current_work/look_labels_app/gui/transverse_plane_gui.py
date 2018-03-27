import tkinter as tk

from PIL import Image, ImageTk

from current_work.look_labels_app.utils.Clock import Clock
from current_work.look_labels_app.utils.ImageProcessor import norm_image, threshold_image, gen_fuse_arr


class TransversePlaneGUI(tk.Toplevel):
    def __init__(self, hu_arrs, suv_arrs, mask_arrs):
        super().__init__()
        self.top_level = self
        self.top_level.title("Transverse Plane View")
        self.top_level.geometry("1920x1080")
        self.top_level.bind("<Left>", self.prev_image_callback)
        self.top_level.bind("<Right>", self.next_image_callback)
        self.top_level.focus_set()

        self.hu_arrs = hu_arrs
        self.suv_arrs = suv_arrs
        self.mask_arrs = mask_arrs
        self.current_index = -1  # 当前图片索引
        self.total_img_num = -1  # 共有多少组图片
        self.clock = Clock(0.12)  # 设置最小键盘事件触发间隔

        # ct frame
        self.ct_frame = tk.Frame(self.top_level, width=512, height=512)
        self.ct_frame.propagate(False)
        self.ct_frame.grid(row=0, column=0)
        self.ct_canvas = tk.Canvas(self.ct_frame, width=512, height=512)
        self.ct_canvas.pack()

        # suv frame
        self.suv_frame = tk.Frame(self.top_level, width=512, height=512)
        self.suv_frame.propagate(False)
        self.suv_frame.grid(row=0, column=1)
        self.suv_canvas = tk.Canvas(self.suv_frame, width=512, height=512)
        self.suv_canvas.bind("<Motion>", self.suv_mouse_move_callback)
        self.suv_canvas.pack()

        # ct & label frame
        self.ctl_frame = tk.Frame(self.top_level, width=512, height=512)
        self.ctl_frame.propagate(False)
        self.ctl_frame.grid(row=1, column=0)
        self.ctl_canvas = tk.Canvas(self.ctl_frame, width=512, height=512)
        self.ctl_canvas.pack()

        # suv & label frame
        self.suvl_frame = tk.Frame(self.top_level, width=512, height=512)
        self.suvl_frame.propagate(False)
        self.suvl_frame.grid(row=1, column=1)
        self.suvl_canvas = tk.Canvas(self.suvl_frame, width=512, height=512)
        self.suvl_canvas.pack()

        # suvt frame
        self.suvt_frame = tk.Frame(self.top_level, width=512, height=512)
        self.suvt_frame.propagate(False)
        self.suvt_frame.grid(row=1, column=2)
        self.suvt_canvas = tk.Canvas(self.suvt_frame, width=512, height=512)
        self.suvt_canvas.pack()

        right_frame = tk.Frame(self.top_level)
        right_frame.propagate(False)
        right_frame.grid(row=0, column=3)
        # 调整SUV阈值
        self.suv_threshold_frame = tk.LabelFrame(right_frame, width=384, text="SUV阈值")
        self.suv_threshold_frame.grid(row=0, column=0)
        self.suv_scale = tk.Scale(self.suv_threshold_frame)
        self.suv_scale.configure(from_=1.0, to=2.5, resolution=0.1, orient=tk.HORIZONTAL,
                                 command=self.suv_scale_callback, length=380)
        self.suv_scale.set(1.5)
        self.suv_scale.pack()
        # 显示图像当前值
        # self.current_img_value_frame = tk.LabelFrame(right_frame, width=384, text="图像实际值")
        # self.current_img_value_frame.grid(row=1, column=0)
        self.current_img_value_label = tk.Label(right_frame)
        self.current_img_value_label.grid(row=1, column=0)

        # 加载后设置变量
        self.total_img_num = len(self.hu_arrs)
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
        ct_arr = norm_image(self.hu_arrs[self.current_index])
        self.current_ct_img = ImageTk.PhotoImage(Image.fromarray(ct_arr, "L"))
        self.ct_canvas.create_image(0, 0, image=self.current_ct_img, anchor=tk.NW)
        self.ct_canvas.create_text(20, 20, text="Hu", fill="yellow", font=("Arial", 20, "normal"), anchor=tk.NW)
        # (row_0, col_1)加载suv
        suv_arr = norm_image(self.suv_arrs[self.current_index])
        self.current_suv_img = ImageTk.PhotoImage(Image.fromarray(suv_arr, "L").resize([512, 512]))
        self.suv_canvas.create_image(0, 0, image=self.current_suv_img, anchor=tk.NW)
        self.suv_canvas.create_text(20, 20, text="SUV", fill="yellow", font=("Arial", 20, "normal"), anchor=tk.NW)

        # 加载mask
        mask_arr = norm_image(self.mask_arrs[self.current_index])
        mask_arr = (mask_arr > 128) * 255

        # (row_1, col_0) 加载ct&label
        self.current_ctl_img = ImageTk.PhotoImage(Image.fromarray(gen_fuse_arr(ct_arr, mask_arr)))
        self.ctl_canvas.create_image(0, 0, image=self.current_ctl_img, anchor=tk.NW)
        self.ctl_canvas.create_text(20, 20, text="Hu & Label", fill="yellow", font=("Arial", 20, "normal"),
                                    anchor=tk.NW)
        # (row_1, col_1) 加载suv&label
        self.current_suvl_img = ImageTk.PhotoImage(Image.fromarray(gen_fuse_arr(suv_arr, mask_arr)))
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
        self.suvt_canvas.create_image(0, 0, image=self.current_thsuv_img, anchor=tk.NW)
        self.suvt_canvas.create_text(20, 20, fill="yellow", font=("Arial", 20, "normal"), anchor=tk.NW,
                                     text="SUV > {}".format(self.suv_scale.get()))

    def suv_mouse_move_callback(self, event):
        """鼠标在图像上移动时，查看值的回调函数"""
        _v = self.suv_arrs[self.current_index][event.y][event.x]
        self.current_img_value_label.configure(text="({:0>3}, {:0>3})= {:.2f}".format(event.x, event.y, _v).ljust(35))
