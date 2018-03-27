import SimpleITK as sitk
from PIL import Image
import numpy as np

# 加载图像
fixed_image_arr = sitk.GetArrayFromImage(sitk.ReadImage("fixedImage.png"))
moving_image_arr = sitk.GetArrayFromImage(sitk.ReadImage("movingImage.png"))
fixed_image = sitk.GetImageFromArray(fixed_image_arr)
moving_image = sitk.GetImageFromArray(moving_image_arr)

# 获得配准映射
parameterMap = sitk.GetDefaultParameterMap("translation")
elastixImageFilter = sitk.ElastixImageFilter()
elastixImageFilter.SetFixedImage(fixed_image)
elastixImageFilter.SetMovingImage(moving_image)
elastixImageFilter.SetParameterMap(parameterMap)
elastixImageFilter.Execute()
resultImage = elastixImageFilter.GetResultImage()
transformParameterMap = elastixImageFilter.GetTransformParameterMap()

# 应用配准映射
transformixImageFilter = sitk.TransformixImageFilter()
transformixImageFilter.SetTransformParameterMap(transformParameterMap)
population = ["movingImage.png"]
for filename in population:
    transformixImageFilter.SetMovingImage(sitk.ReadImage(filename))
    transformixImageFilter.Execute()
    sitk.Show(transformixImageFilter.GetResultImage())
