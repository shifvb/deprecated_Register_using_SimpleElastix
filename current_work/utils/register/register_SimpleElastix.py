import os
import time
import numpy as np
import pydicom
from PIL import Image
import SimpleITK as sitk
from current_work.utils.SUV_calculation.SUVTools import getASuv

__version__ = (0, 4, 0)
__last_modified__ = 1522111810
__author__ = "shifvb"
__email__ = "shifvb@gmail.com"


def register_image_series_pt2ct(ct_series_dir: str, pt_series_dir: str):
    """
    将pet图像序列配准到ct图像序列上
    注意：SimpleElastix读取的是Hu值及SUV值。
    :param ct_series_dir: ct图像序列绝对路径
    :param pt_series_dir: pt图像序列绝对路径
    :return: 配准后的SUV图像序列数组，原CT图像Hu值序列数组，原PT图像SUV值序列数组
        class ：np.ndarray
        dtype ：np.float32
        shape ：(图像序列数, 配准后图像高度, 配准后图像宽度)
            若将200张分辨率为128x128的pet图像配准到200张分辨率为512x512的ct图像上，
            则返回数组的shape为(200, 512, 512)
    """
    # step_1. load image series
    _original_dir = os.path.abspath(os.curdir)
    os.chdir(ct_series_dir)
    hu_images = sitk.ReadImage(os.listdir(ct_series_dir))
    os.chdir(pt_series_dir)
    suv_images = sitk.ReadImage(os.listdir(pt_series_dir))
    os.chdir(_original_dir)

    # step_2. set register parameters
    parameter_map = sitk.GetDefaultParameterMap("translation")
    parameter_map['RequiredRatioOfValidSamples'] = ['0.05']

    # step_3. set up image filter
    elastix_image_filter = sitk.ElastixImageFilter()
    elastix_image_filter.SetFixedImage(hu_images)
    elastix_image_filter.SetMovingImage(suv_images)
    elastix_image_filter.SetParameterMap(parameter_map)

    # step_4. register
    elastix_image_filter.Execute()

    # step_5. get register result
    result_image = elastix_image_filter.GetResultImage()
    registered_suv_arrs = sitk.GetArrayFromImage(result_image)
    hu_arrs = sitk.GetArrayFromImage(hu_images)
    suv_arrs = sitk.GetArrayFromImage(suv_images)

    # step_6. normalize suv arrs
    ratio = _get_ratio(pt_series_dir)
    registered_suv_arrs /= ratio
    suv_arrs /= ratio

    return registered_suv_arrs, hu_arrs, suv_arrs


def _get_ratio(pt_series_dir: str):
    """
    因为simpleElastix加载pt文件得出的值和SUVlbm之间只差了一个系数k，
    此函数用于计算这个系数(k是常数，每个病例中所有slice中的k相同)
    :param pt_series_dir: pt文件夹绝对路径
    :return: k的值
    """
    pt_file_name = os.listdir(pt_series_dir)[0]
    # load image using SimpleElastix
    _original_dir = os.curdir
    os.chdir(pt_series_dir)
    sitk_arr = sitk.GetArrayFromImage(sitk.ReadImage(pt_file_name))
    os.chdir(_original_dir)
    # load image using li's suv calculation
    li_arr = getASuv(pt_file_name)
    # return ratio
    return sitk_arr.mean() / li_arr.mean()


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
