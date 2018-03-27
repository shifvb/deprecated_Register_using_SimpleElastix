import SimpleITK as sitk

# 加载图像
fixed_image_arr = sitk.GetArrayFromImage(sitk.ReadImage("fixed_image.png"))
moving_image_arr = sitk.GetArrayFromImage(sitk.ReadImage("moving_image.png")).transpose([2, 0, 1])[0]
fixed_image = sitk.GetImageFromArray(fixed_image_arr)
moving_image = sitk.GetImageFromArray(moving_image_arr)
sitk.Show(fixed_image)
sitk.Show(moving_image)
#
elastixImageFilter = sitk.ElastixImageFilter()
elastixImageFilter.SetFixedImage(fixed_image)
elastixImageFilter.SetMovingImage(moving_image)
elastixImageFilter.SetParameterMap(sitk.GetDefaultParameterMap("affine"))
elastixImageFilter.Execute()
sitk.Show(elastixImageFilter.GetResultImage())

