import os
from copy import deepcopy
import tkinter as tk
from tkinter.font import Font
from tkinter import filedialog
from current_work.utils.load_data import load_data
from current_work.look_labels_app.gui import CoronalPlaneGUI, TransversePlaneGUI
from current_work.utils.SUV_calculation import getBaseInfo


class MainGUI(object):
    def __init__(self, config: dict):
        self.root = tk.Tk()
        self.config = config
        self.big_font = Font(size=20)
        self.mid_font = Font(size=15)

        self.is_loaded = False
        self.ct_arrs = None
        self.pt_arrs = None
        self.suv_arrs = None
        self.mask_arrs = None
        self.patient_info_ct = None
        self.patient_info_pt = None

        # choose folder entry
        self.load_dir_frame = tk.LabelFrame(self.root, text="load file")
        self.load_dir_frame.grid(row=0, column=0, sticky=tk.NW, padx=5)
        self.load_dir_var = tk.StringVar(value=self.config["default_load_path"] if self.config["debug"] else "")
        self.load_dir_entry = tk.Entry(self.load_dir_frame, width=25, font=self.big_font,
                                       textvariable=self.load_dir_var)
        self.load_dir_entry.grid(row=0, column=0, columnspan=2, padx=5)
        self.select_dir_btn = tk.Button(self.load_dir_frame, text="choose dir", font=self.mid_font,
                                        command=self.select_dir_btn_callback, width=12)
        self.select_dir_btn.grid(row=1, column=0, pady=5)
        self.load_dir_btn = tk.Button(self.load_dir_frame, text="load", font=self.mid_font,
                                      command=self.load_dir_btn_callback, width=12)
        self.load_dir_btn.grid(row=1, column=1)

        # 加载冠状面
        tk.Button(self.root, text="加载冠状面", command=self.load_coronal_plane).grid(row=1, column=0)
        # 加载横断面
        tk.Button(self.root, text="加载横断面", command=self.load_transverse_plane).grid(row=2, column=0)
        tk.mainloop()

    def load_dir_btn_callback(self):
        """用户点击加载按钮回调函数"""
        # 确定ct，pt，mask文件夹位置
        path = self.load_dir_var.get()
        mask_path = os.path.join(path, "mask")
        ct_path = os.path.join(path, "CT")
        pt_path = os.path.join(path, "PT")

        # 加载图像序列
        _ = load_data(ct_path, pt_path, mask_path, buffer_mode=True, work_directory=path,
                      temp_dir_name=self.config["temp_dir_name"])
        self.ct_arrs, self.pt_arrs, self.suv_arrs, self.mask_arrs = _
        # 加载病人基本信息
        self.patient_info_ct = deepcopy(getBaseInfo(ct_path))
        self.patient_info_pt = deepcopy(getBaseInfo(pt_path))

        self.is_loaded = True

    def select_dir_btn_callback(self):
        """用户点击选择文件夹按钮回调函数"""
        self.load_dir_var.set(filedialog.askdirectory())

    def load_coronal_plane(self):
        """加载冠状面病人图像"""
        CoronalPlaneGUI(self.ct_arrs, self.pt_arrs, self.mask_arrs, self.patient_info_ct) if self.is_loaded else None

    def load_transverse_plane(self):
        """加载横断面病人图像"""
        TransversePlaneGUI(self.ct_arrs, self.suv_arrs, self.mask_arrs) if self.is_loaded else None
