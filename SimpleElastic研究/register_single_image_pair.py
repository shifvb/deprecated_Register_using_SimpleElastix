import numpy as np
from PIL import Image
import SimpleITK as sitk

__version__ = (0, 1, 0)
__last_modified__ = 1520236584
__author__ = "shifvb"
__email__ = "shifvb@gmail.com"


def register_single_image_pair(fixed_image_arr: np.ndarray, moving_image_arr: np.ndarray,
                               parameter_map_str="translation"):
    """
    端到端配准(仅一对图像)
    :param fixed_image_arr: 原图像（一张）， numpy arr类型
    :param moving_image_arr: 要被配准的图像（一张），numpy arr类型
    :param parameter_map_str: 配准方法，默认为translation(截至目前我都不知道这是什么，具体的看文档
        http://simpleelastix.readthedocs.io/)
    :return: 配准结果的 numpy arr, 以及定义配准的parameter map
    """
    parameter_map = sitk.GetDefaultParameterMap(parameter_map_str)

    # elastix image filter
    elastix_image_filter = sitk.ElastixImageFilter()  # 初始化一个elastix image filter
    elastix_image_filter.SetFixedImage(sitk.GetImageFromArray(fixed_image_arr))  # 设定原图像
    elastix_image_filter.SetMovingImage(sitk.GetImageFromArray(moving_image_arr))  # 设定要被配准的图像
    elastix_image_filter.SetParameterMap(parameter_map)  # 设定参数（配准方法）
    elastix_image_filter.Execute()

    # get result
    result_image = elastix_image_filter.GetResultImage()
    result_arr = sitk.GetArrayFromImage(result_image)
    return result_arr, parameter_map


def main():
    # 生成原图像numpy array
    fixed_image_path = "fixedImage.png"
    fixed_image = Image.open(open(fixed_image_path, 'rb'))
    fixed_image_arr = np.array(fixed_image)
    print("fixed_image:", fixed_image_arr.dtype, fixed_image_arr.shape)

    # 生成配准图像numpy array
    moving_image_path = "movingImage.png"
    moving_image = Image.open(open(moving_image_path, 'rb'))
    moving_image_arr = np.array(moving_image)
    print("moving_image:", moving_image_arr.dtype, moving_image_arr.shape)

    # 配准
    result_arr = register_single_image_pair(fixed_image, moving_image)[0]
    result_arr = 255 - result_arr
    print(result_arr.dtype, result_arr.shape)
    Image.fromarray(result_arr).show()


if __name__ == '__main__':
    main()
