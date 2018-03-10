import os
import time
import tkinter as tk
from tkinter import filedialog
import numpy as np
import SimpleITK as sitk
from PIL import Image, ImageTk

from SimpleElastic研究.register_image_series import register_image_series_pt2ct as register
from 查看PTCT及标签数据 import look_labels_app as APP
from 查看PTCT及标签数据._utils.ImageProcessor import norm_image, threshold_image
from 查看PTCT及标签数据._utils.SUVTools import getRegistedSUVs

_last_load_img_time = time.time()
_key_press_interval = 0.1


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

    # 根据文件夹位置加载图像序列
    _curdir = os.path.abspath(os.curdir)
    APP.I.pt_arrs, APP.I.ct_arrs, _ = register(ct_path, pt_path)  # load ct & pt
    APP.I.suv_arrs = getRegistedSUVs(APP.I.pt_arrs, pt_path)  # calculate suv
    os.chdir(mask_path)  # load mask
    APP.I.mask_arrs = sitk.GetArrayFromImage(sitk.ReadImage(os.listdir(mask_path)))
    os.chdir(_curdir)

    # 加载后设置变量
    APP.I.total_img_num = len(APP.I.ct_arrs)
    APP.I.is_loaded = True
    APP.I.current_index = 0

    # 加载图像
    _load_images()


def prev_image_callback(event=None):
    """用户点击上一张按钮回调函数"""
    if APP.I.is_loaded is False:  # 没加载return
        return
    global _last_load_img_time
    if time.time() - _last_load_img_time < _key_press_interval:
        return
    _last_load_img_time = time.time()
    if APP.I.current_index <= 0:  # 越界reutrn
        APP.I.current_index = APP.I.total_img_num
    APP.I.current_index -= 1
    _load_images()


def next_image_callback(event=None):
    """用户点击下一张按钮回掉函数"""
    if APP.I.is_loaded is False:  # 没加载return
        return
    global _last_load_img_time
    if time.time() - _last_load_img_time < _key_press_interval:
        return
    _last_load_img_time = time.time()
    if APP.I.current_index >= APP.I.total_img_num - 1:  # 越界reutrn
        APP.I.current_index = -1
    APP.I.current_index += 1
    _load_images()


def _load_images():
    """加载界面图像"""
    # (row_0, col_0) 加载ct
    ct_arr = norm_image(APP.I.ct_arrs[APP.I.current_index])
    APP.I.current_ct_img = ImageTk.PhotoImage(Image.fromarray(ct_arr, "L"))
    APP.I.ct_canvas.create_image(0, 0, image=APP.I.current_ct_img, anchor=tk.NW)
    APP.I.ct_canvas.create_text(20, 20, text="CT", fill="yellow", font=("Arial", 20, "normal"), anchor=tk.NW)
    # (row_0, col_1) 加载pt
    pt_arr = norm_image(APP.I.pt_arrs[APP.I.current_index])
    APP.I.current_pt_img = ImageTk.PhotoImage(Image.fromarray(pt_arr, "L"))
    APP.I.pt_canvas.create_image(0, 0, image=APP.I.current_pt_img, anchor=tk.NW)
    APP.I.pt_canvas.create_text(20, 20, text="PET", fill="yellow", font=("Arial", 20, "normal"), anchor=tk.NW)
    # (row_0, col_2)加载suv
    suv_arr = norm_image(APP.I.suv_arrs[APP.I.current_index])
    APP.I.current_suv_img = ImageTk.PhotoImage(Image.fromarray(suv_arr, "L").resize([512, 512]))
    APP.I.suv_canvas.create_image(0, 0, image=APP.I.current_suv_img, anchor=tk.NW)
    APP.I.suv_canvas.create_text(20, 20, text="SUV", fill="yellow", font=("Arial", 20, "normal"), anchor=tk.NW)

    # 加载mask
    mask_arr = norm_image(APP.I.mask_arrs[APP.I.current_index])

    # (row_1, col_0) 加载ct&label
    arr_0 = np.array(ct_arr)
    arr_1 = (np.array(mask_arr)[:, :, 0] > 128) * 255
    arr_2 = np.empty(shape=[3, arr_0.shape[0], arr_0.shape[1]], dtype=np.uint8)
    arr_2[0] = (arr_0 + arr_1) / 2  # R通道
    arr_2[1] = arr_0  # G通道
    arr_2[2] = arr_1  # B通道
    arr_2 = arr_2.transpose([1, 2, 0])
    APP.I.current_ctl_img = ImageTk.PhotoImage(Image.fromarray(arr_2, "RGB"))
    APP.I.ctl_canvas.create_image(0, 0, image=APP.I.current_ctl_img, anchor=tk.NW)
    APP.I.ctl_canvas.create_text(20, 20, text="CT & Label", fill="yellow", font=("Arial", 20, "normal"), anchor=tk.NW)
    # (row_1, col_1) 加载pt&label
    arr_0 = np.array(pt_arr)
    arr_1 = (np.array(mask_arr)[:, :, 0] > 128) * 255
    arr_2 = np.empty(shape=[3, arr_0.shape[0], arr_0.shape[1]], dtype=np.uint8)
    arr_2[0] = (arr_0 + arr_1) / 2  # R通道
    arr_2[1] = arr_0  # G通道
    arr_2[2] = arr_1  # B通道
    arr_2 = arr_2.transpose([1, 2, 0])
    APP.I.current_ptl_img = ImageTk.PhotoImage(Image.fromarray(arr_2, "RGB"))
    APP.I.ptl_canvas.create_image(0, 0, image=APP.I.current_ptl_img, anchor=tk.NW)
    APP.I.ptl_canvas.create_text(20, 20, text="PET & Label", fill="yellow", font=("Arial", 20, "normal"), anchor=tk.NW)
    # (row_1, col_2) 加载suv > 1.5
    suv_scale_callback()

    # 设置title
    APP.I.root.title("当前图像: {}/{}".format(APP.I.current_index + 1, APP.I.total_img_num))


def suv_scale_callback(*args):
    if APP.I.is_loaded is False:
        return
    thsuv_arr = threshold_image(APP.I.suv_arrs[APP.I.current_index], APP.I.suv_scale.get()) * 255
    APP.I.current_thsuv_img = ImageTk.PhotoImage(Image.fromarray(thsuv_arr, "L"))
    APP.I.label_canvas.create_image(0, 0, image=APP.I.current_thsuv_img, anchor=tk.NW)
    APP.I.label_canvas.create_text(20, 20, fill="yellow", font=("Arial", 20, "normal"), anchor=tk.NW,
                                   text="SUV > {}".format( APP.I.suv_scale.get()))
