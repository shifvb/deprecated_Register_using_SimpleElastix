import tkinter as tk
from tkinter.font import Font

from current_work.look_labels_app.tk_callbacks import prev_image_callback, next_image_callback, suv_scale_callback
from current_work.look_labels_app.tk_callbacks import select_dir_btn_callback, load_dir_btn_callback

I = None  # "I" for instance


class LookLabelAPP(object):
    def __init__(self, config: dict):
        global I
        I = self
        self.root = tk.Tk()
        self.root.bind("<Left>", prev_image_callback)
        self.root.bind("<Right>", next_image_callback)
        self.config = config
        self.is_loaded = False
        self.current_index = -1  # 当前图片索引
        self.total_img_num = -1  # 共有多少组图片

        # ct frame
        self.ct_frame = tk.Frame(self.root, width=512, height=512)
        self.ct_frame.propagate(False)
        self.ct_frame.grid(row=0, column=0)
        self.ct_canvas = tk.Canvas(self.ct_frame, width=512, height=512)
        self.ct_canvas.pack()

        # ct & label frame
        self.ctl_frame = tk.Frame(self.root, width=512, height=512)
        self.ctl_frame.propagate(False)
        self.ctl_frame.grid(row=1, column=0)
        self.ctl_canvas = tk.Canvas(self.ctl_frame, width=512, height=512)
        self.ctl_canvas.pack()

        # suv frame
        self.suv_frame = tk.Frame(self.root, width=512, height=512)
        self.suv_frame.propagate(False)
        self.suv_frame.grid(row=0, column=1)
        self.suv_canvas = tk.Canvas(self.suv_frame, width=512, height=512)
        self.suv_canvas.pack()

        # suv & label frame
        self.suvl_frame = tk.Frame(self.root, width=512, height=512)
        self.suvl_frame.propagate(False)
        self.suvl_frame.grid(row=1, column=1)
        self.suvl_canvas = tk.Canvas(self.suvl_frame, width=512, height=512)
        self.suvl_canvas.pack()

        # label frame
        self.label_frame = tk.Frame(self.root, width=512, height=512)
        self.label_frame.propagate(False)
        self.label_frame.grid(row=1, column=2)
        self.label_canvas = tk.Canvas(self.label_frame, width=512, height=512)
        self.label_canvas.pack()

        # right frame
        right_frame = tk.Frame(self.root)
        right_frame.propagate(False)
        right_frame.grid(row=0, rowspan=2, column=3, sticky=tk.NW)

        # choose folder entry
        self.load_dir_frame = tk.LabelFrame(right_frame, width=384, height=128, text="load file")
        self.load_dir_frame.propagate(False)
        self.load_dir_frame.grid(row=0, column=0, sticky=tk.NW)
        self.load_dir_var = tk.StringVar(value=self.config["default_load_path"] if self.config["debug"] else "")
        self.load_dir_entry = tk.Entry(self.load_dir_frame, width=25, font=Font(size=20),
                                       textvariable=self.load_dir_var)
        self.load_dir_entry.pack(side=tk.TOP, padx=5)
        self.select_dir_btn = tk.Button(self.load_dir_frame, text="choose dir", font=Font(size=15),
                                        command=select_dir_btn_callback, width=15)
        self.select_dir_btn.pack(side=tk.TOP)
        self.load_dir_btn = tk.Button(self.load_dir_frame, text="load", font=Font(size=15),
                                      command=load_dir_btn_callback, width=15)
        self.load_dir_btn.pack(side=tk.TOP, padx=5)

        # 调整SUV阈值
        self.suv_threshold_frame = tk.LabelFrame(right_frame, width=384, text="SUV阈值")
        # self.suv_threshold_frame.propagate(False)
        self.suv_threshold_frame.grid(row=1, column=0)
        self.suv_scale = tk.Scale(self.suv_threshold_frame)
        self.suv_scale.configure(from_=1.0, to=2.5, resolution=0.1, orient=tk.HORIZONTAL, command=suv_scale_callback,
                                 length=380)
        self.suv_scale.set(1.5)
        self.suv_scale.pack()

        tk.mainloop()
