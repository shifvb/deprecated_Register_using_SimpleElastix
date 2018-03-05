import tkinter as tk
from tkinter.font import Font
from 查看PTCT及标签数据.tk_callbacks import select_dir_btn_callback, load_dir_btn_callback
from 查看PTCT及标签数据.tk_callbacks import prev_image_callback, next_image_callback

I = None  # "I" for instance


class LookLabelAPP(object):
    def __init__(self, config: dict):
        global I
        I = self
        self.root = tk.Tk()
        self.root.bind("<Left>", prev_image_callback)
        self.root.bind("<Right>", next_image_callback)
        # self.root.geometry("1920x1010-0+0")
        self.config = config
        self.is_loaded = False
        self.current_index = -1  # 当前图片索引
        self.total_img_num = -1  # 共有多少组图片
        self.abs_mask_list = list()  # mask path list(absolute)
        self.abs_ct_list = list()  # mask ct list(absolute)
        self.abs_pt_list = list()  # mask pt list(absolute)

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

        # pt frame
        self.pt_frame = tk.Frame(self.root, width=512, height=512)
        self.pt_frame.propagate(False)
        self.pt_frame.grid(row=0, column=1)
        self.pt_canvas = tk.Canvas(self.pt_frame, width=512, height=512)
        self.pt_canvas.pack()

        # pt & label frame
        self.ptl_frame = tk.Frame(self.root, width=512, height=512)
        self.ptl_frame.propagate(False)
        self.ptl_frame.grid(row=1, column=1)
        self.ptl_canvas = tk.Canvas(self.ptl_frame, width=512, height=512)
        self.ptl_canvas.pack()

        # label frame
        self.label_frame = tk.Frame(self.root, width=512, height=512)
        self.label_frame.propagate(False)
        self.label_frame.grid(row=0, column=2)
        self.label_canvas = tk.Canvas(self.label_frame, width=512, height=512)
        self.label_canvas.pack()

        # choose folder entry
        self.load_dir_frame = tk.Frame(self.root, width=384, height=128)
        self.load_dir_frame.propagate(False)
        self.load_dir_frame.grid(row=0, column=3)
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

        # page control frame
        self.page_ctrl_frame = tk.Frame(self.root, width=384, height=30)
        self.page_ctrl_frame.propagate(False)
        self.page_ctrl_frame.grid(row=1, column=3, sticky=tk.NS)
        self.prev_btn = tk.Button(self.page_ctrl_frame, text="prev image", font=Font(size=15),
                                  command=prev_image_callback)

        self.next_btn = tk.Button(self.page_ctrl_frame, text="next image", font=Font(size=15),
                                  command=next_image_callback)

        self.next_btn.pack(side=tk.RIGHT)
        self.prev_btn.pack(side=tk.RIGHT)

        tk.mainloop()
