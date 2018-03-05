import os
import tkinter as tk
from tkinter import filedialog
import dicom
import numpy as np
from PIL import Image, ImageTk
import time
from 查看PTCT及标签数据 import look_labels_app as APP
from 查看PTCT及标签数据._utils.ImageProcessor import ImageProcessor

image_processor = ImageProcessor()
_last_load_img_time = time.time()


def select_dir_btn_callback():
    """用户点击选择文件夹按钮回调函数"""
    path = filedialog.askdirectory()
    APP.I.load_dir_var.set(path)


def load_dir_btn_callback():
    """用户点击加载按钮回调函数"""
    # 确定ct，pt，mask文件夹位置
    path = APP.I.load_dir_var.get()
    mask_path = os.path.join(path, "mask")
    ct_path = os.path.join(path, "CT")
    pt_path = os.path.join(path, "PT")
    # load mask
    APP.I.abs_mask_list = [os.path.join(mask_path, _) for _ in os.listdir(mask_path)]
    APP.I.total_img_num = len(APP.I.abs_mask_list)
    # load ct
    APP.I.abs_ct_list = [os.path.join(ct_path, _) for _ in os.listdir(ct_path)]
    # load pt
    APP.I.abs_pt_list = [os.path.join(pt_path, _) for _ in os.listdir(pt_path)]
    # 加载后设置变量
    APP.I.is_loaded = True
    APP.I.current_index = 0
    # 加载图像
    _load_images()


def prev_image_callback(event=None):
    """用户点击上一张按钮回调函数"""
    if APP.I.is_loaded is False:  # 没加载return
        return
    global _last_load_img_time
    if time.time() - _last_load_img_time <= 0.14:  # 限制调用频率
        return
    _last_load_img_time = time.time()
    if APP.I.current_index <= 0:  # 越界reutrn
        return
    APP.I.current_index -= 1
    _load_images()


def next_image_callback(event=None):
    """用户点击下一张按钮回掉函数"""
    if APP.I.is_loaded is False:  # 没加载return
        return
    global _last_load_img_time
    if time.time() - _last_load_img_time <= 0.14:  # 限制调用频率
        return
    _last_load_img_time = time.time()
    if APP.I.current_index >= APP.I.total_img_num - 1:  # 越界reutrn
        return
    APP.I.current_index += 1
    _load_images()


def _load_images():
    """加载界面图像"""
    # 加载ct
    abs_ct_path = APP.I.abs_ct_list[APP.I.current_index]
    ct_data = dicom.read_file(abs_ct_path)
    ct_arr = image_processor.cal_Hu(ct_data.pixel_array, ct_data.RescaleSlope, ct_data.RescaleIntercept)
    ct_arr = image_processor.norm_image(ct_arr)
    APP.I.current_ct_img = ImageTk.PhotoImage(Image.fromarray(ct_arr, "L"))
    APP.I.ct_canvas.create_image(0, 0, image=APP.I.current_ct_img, anchor=tk.NW)
    # 加载pt
    abs_pt_path = APP.I.abs_pt_list[APP.I.current_index]
    pt_arr = image_processor.cal_SUV(abs_pt_path)
    pt_arr = image_processor.norm_image(pt_arr)
    pt_img = Image.fromarray(pt_arr, "L").resize([512, 512])
    pt_arr = 255 - np.array(pt_img)
    APP.I.current_pt_img = ImageTk.PhotoImage(Image.fromarray(pt_arr, "L"))
    APP.I.pt_canvas.create_image(0, 0, image=APP.I.current_pt_img, anchor=tk.NW)
    # 加载mask
    abs_mask_path = APP.I.abs_mask_list[APP.I.current_index]
    APP.I.current_mask_img = ImageTk.PhotoImage(Image.open(abs_mask_path))
    APP.I.label_canvas.create_image(0, 0, image=APP.I.current_mask_img, anchor=tk.NW)
    APP.I.root.title("当前图像: {}/{}".format(APP.I.current_index + 1, APP.I.total_img_num))
    # 加载ct&label
    arr_0 = np.array(ct_arr)
    arr_1 = np.array(Image.open(abs_mask_path))[:, :, 0] > 128  # R通道
    arr_2 = (arr_0 * (1 - arr_1)).astype(dtype=np.uint8)
    APP.I.current_ctl_img = ImageTk.PhotoImage(Image.fromarray(arr_2, "L"))
    APP.I.ctl_canvas.create_image(0, 0, image=APP.I.current_ctl_img, anchor=tk.NW)
    # 加载pt&label
    arr_0 = np.array(pt_arr)
    arr_1 = np.array(Image.open(abs_mask_path))[:, :, 0] > 128  # R通道
    arr_2 = (arr_0 * (1 - arr_1)).astype(dtype=np.uint8)
    APP.I.current_ptl_img = ImageTk.PhotoImage(Image.fromarray(arr_2, "L"))
    APP.I.ptl_canvas.create_image(0, 0, image=APP.I.current_ptl_img, anchor=tk.NW)
