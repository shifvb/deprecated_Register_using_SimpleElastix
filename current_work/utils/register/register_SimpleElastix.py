import os
import time
import numpy as np
import pydicom
from PIL import Image
import SimpleITK as sitk

__version__ = (0, 3, 0)
__last_modified__ = 1520499603
__author__ = "shifvb"
__email__ = "shifvb@gmail.com"


def register_image_series_pt2ct(ct_series_dir: str, pt_series_dir: str):
    """
    将pet图像序列配准到ct图像序列上
    :param ct_series_dir: ct图像序列绝对路径
    :param pt_series_dir: pt图像序列绝对路径
    :return: 配准后的SUV图像序列数组，原CT图像Hu值序列数组，原PT图像加权后SUV值序列数组
        class ：np.ndarray
        dtype ：np.float32
        shape ：(图像序列数, 配准后图像高度, 配准后图像宽度)
            若将200张分辨率为128x128的pet图像配准到200张分辨率为512x512的ct图像上，
            则返回数组的shape为(200, 512, 512)
    """
    # 0. 加载图像序列
    _original_dir = os.path.abspath(os.curdir)
    os.chdir(ct_series_dir)
    Hu_imgs = sitk.ReadImage(os.listdir(ct_series_dir))
    os.chdir(pt_series_dir)
    SUV_imgs = sitk.ReadImage(os.listdir(pt_series_dir))
    os.chdir(_original_dir)
    # 1. 设置配准参数
    parameter_map = sitk.GetDefaultParameterMap("translation")
    parameter_map['RequiredRatioOfValidSamples'] = ['0.05']
    # 2. 初始化filter并设置参数
    elastix_image_filter = sitk.ElastixImageFilter()
    elastix_image_filter.SetFixedImage(Hu_imgs)
    elastix_image_filter.SetMovingImage(SUV_imgs)
    elastix_image_filter.SetParameterMap(parameter_map)
    # 3. 进行配准计算
    elastix_image_filter.Execute()
    # 4. 得出配准结果
    result_image = elastix_image_filter.GetResultImage()
    return sitk.GetArrayFromImage(result_image), sitk.GetArrayFromImage(Hu_imgs), sitk.GetArrayFromImage(SUV_imgs)


def main():
    # 配准
    result = register_image_series_pt2ct(ct_series_dir=r"F:\做好的分割数据\迟学梅\CT",
                                         pt_series_dir=r"F:\做好的分割数据\迟学梅\PT")
    sitk.Show(sitk.GetImageFromArray(result[0]))
    sitk.Show(sitk.GetImageFromArray(result[1]))
    sitk.Show(sitk.GetImageFromArray(result[2]))


if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    print("time elapsed: {}".format(end_time - start_time))
