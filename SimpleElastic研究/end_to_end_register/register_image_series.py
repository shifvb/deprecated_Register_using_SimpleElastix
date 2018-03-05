import os
import numpy as np
import dicom
from PIL import Image
import SimpleITK as sitk
from SimpleElastic研究.end_to_end_register.register_single_image_pair import register_single_image_pair
from 查看PTCT及标签数据._utils.ImageProcessor import ImageProcessor

I = ImageProcessor()
__version__ = (0, 1, 0)
__last_modified__ = 1520254969
__author__ = "shifvb"
__email__ = "shifvb@gmail.com"


def register_image_series_pet_to_ct():
    # 1. 加载文件
    ct_series_dir = r"F:\做好的分割数据\迟学梅\CT"
    pt_series_dir = r"F:\做好的分割数据\迟学梅\PT"
    ct_series_names = [os.path.join(ct_series_dir, _) for _ in os.listdir(ct_series_dir)]
    pt_series_names = [os.path.join(pt_series_dir, _) for _ in os.listdir(pt_series_dir)]
    register_img_index = 100
    register_ct_img_arr = dicom.read_file(ct_series_names[register_img_index]).pixel_array
    register_pt_img_arr = dicom.read_file(pt_series_names[register_img_index]).pixel_array
    # Image.fromarray(I.norm_image(register_ct_img_arr)).show()
    # Image.fromarray(I.norm_image(register_pt_img_arr)).show()
    # 2.开始配准
    fixed_image = sitk.GetImageFromArray(register_ct_img_arr)
    moving_image = sitk.GetImageFromArray(register_pt_img_arr)
    parameter_map = sitk.GetDefaultParameterMap("translation")
    parameter_map['RequiredRatioOfValidSamples'] = ['0.05']
    # 2.1 设置filter
    elastix_image_filter = sitk.ElastixImageFilter()
    elastix_image_filter.SetFixedImage(fixed_image)
    elastix_image_filter.SetMovingImage(moving_image)
    elastix_image_filter.SetParameterMap(parameter_map)
    # 2.2 进行配准计算，得出配准结果
    elastix_image_filter.Execute()
    result_image = elastix_image_filter.GetResultImage()
    Image.fromarray(255 - sitk.GetArrayFromImage(result_image)).show()


def main():
    register_image_series_pet_to_ct()


if __name__ == '__main__':
    main()
