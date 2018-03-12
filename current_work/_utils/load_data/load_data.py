import os
import SimpleITK as sitk
from current_work._utils.register.register_SimpleElastix import register_image_series_pt2ct as register
from current_work._utils.SUV_calculation.SUVTools import getRegistedSUVs

def load_data(ct_path, pt_path, mask_path):
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
