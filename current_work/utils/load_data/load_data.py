import os
import pickle
import SimpleITK as sitk
from current_work.utils.register.register_SimpleElastix import register_image_series_pt2ct as register
from current_work.utils.SUV_calculation.SUVTools import getRegistedSUVs


def _load_data(ct_path: str, pt_path: str, mask_path: str):
    """
    加载数据，将pt配准到ct上
    :param ct_path: ct绝对路径
    :param pt_path: pt绝对路径
    :param mask_path: mask绝对路径
    :return: ct数组，pt数组，suv数组，mask数组
    """
    # (1) load ct & pt
    pt_arrs, ct_arrs, _ = register(ct_path, pt_path)
    # (2) calculate suv
    suv_arrs = getRegistedSUVs(pt_arrs, pt_path)
    # (3) load mask
    _curdir = os.path.abspath(os.curdir)
    os.chdir(mask_path)
    mask_arrs = sitk.GetArrayFromImage(sitk.ReadImage(os.listdir(mask_path)))
    os.chdir(_curdir)
    return ct_arrs, pt_arrs, suv_arrs, mask_arrs


def load_data(ct_path: str, pt_path: str, mask_path: str, buffer_mode=True, work_directory=None, temp_dir_name=None):
    # 如果不开启缓存模式直接读取数据并配准
    if not buffer_mode:
        return _load_data(ct_path, pt_path, mask_path)
    # 如果文件夹不存在创建文件夹
    _temp_dir = os.path.join(work_directory, temp_dir_name)
    _temp_filename = os.path.join(_temp_dir, "registered.pydump")
    if not os.path.isdir(_temp_dir):
        os.mkdir(_temp_dir)
    # 如果开启缓存模式，且没有缓存，那么就写入缓存
    if not os.path.exists(_temp_filename):
        pickle.dump(_load_data(ct_path, pt_path, mask_path), open(_temp_filename, 'wb'))
    # 读取缓存
    return pickle.load(open(_temp_filename, 'rb'))
