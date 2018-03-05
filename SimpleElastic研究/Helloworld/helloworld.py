import SimpleITK as sitk
import matplotlib.pyplot as plt
import pylab
import numpy as np
from PIL import Image


def main():
    # load image & parameter map
    fixed_image = sitk.ReadImage("fixedImage.png")
    moving_image = sitk.ReadImage("movingImage.png")
    parameter_map = sitk.GetDefaultParameterMap("translation")

    # elastix image filter
    elastix_image_filter = sitk.ElastixImageFilter()
    elastix_image_filter.SetFixedImage(fixed_image)
    elastix_image_filter.SetMovingImage(moving_image)
    elastix_image_filter.SetParameterMap(parameter_map)
    elastix_image_filter.Execute()
    resultImage = elastix_image_filter.GetResultImage()
    transform_parameter_map = elastix_image_filter.GetTransformParameterMap()

    # tranfix image filter
    transfix_image_filter = sitk.TransformixImageFilter()
    transfix_image_filter.SetTransformParameterMap(transform_parameter_map)
    population = ['movingImage.png']
    for filename in population:
        transfix_image_filter.SetMovingImage(sitk.ReadImage(filename))
        transfix_image_filter.Execute()
        array = sitk.GetArrayFromImage(transfix_image_filter.GetResultImage())
        array = array.astype(np.uint8)
        print(array.shape, array.dtype)
        image = Image.fromarray(array, "L")
        # image.show()
        image.save(open("result.png", "wb"))

        # 解决plt.imshow()函数失效问题
        # plt.imshow(array)
        # pylab.show()


if __name__ == '__main__':
    main()
