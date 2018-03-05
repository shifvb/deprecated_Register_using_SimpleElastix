import SimpleITK as sitk
import sys, os



def get_registration_parameters():
    """获取配准参数"""
    fixedImage = sitk.ReadImage(
        r'F:\temp\Chi_Xuemei\18711_004_Body_+_Std_20170411\Chi_Xuemei_20170411_18711_004_10_1_PET_CT_3D_WB_Body_+_Std.hdr')
    sitk.Show(fixedImage)
    movingImage = sitk.ReadImage(
        r'F:\temp\Chi_Xuemei\18711_005_WB_3D_20170411\Chi_Xuemei_20170411_18711_005_PET_CT_3D_WB_WB_3D_0.hdr')
    parameterMap = sitk.GetDefaultParameterMap('translation')
    parameterMap['RequiredRatioOfValidSamples'] = ['0.05']  # 不加这个不好使
    # 设置filter
    elastixImageFilter = sitk.ElastixImageFilter()
    elastixImageFilter.SetFixedImage(fixedImage)
    elastixImageFilter.SetMovingImage(movingImage)
    elastixImageFilter.SetParameterMap(parameterMap)
    elastixImageFilter.Execute()
    # 获取配准参数
    return elastixImageFilter.GetTransformParameterMap()

    # resultImage = elastixImageFilter.GetResultImage()
    # sitk.Show(resultImage)
    # sitk.WriteImage(resultImage)


def apply_registration_parameters(parameter_map):
    """
    应用配准结果
    :param parameter_map: 配准好的参数
    :return: None
    """
    transformixImageFilter = sitk.TransformixImageFilter()
    transformixImageFilter.SetTransformParameterMap(parameter_map)
    population = [r'F:\temp\Chi_Xuemei\18711_005_WB_3D_20170411\Chi_Xuemei_20170411_18711_005_PET_CT_3D_WB_WB_3D_0.hdr',
                  r'F:\temp\Chi_Xuemei\18711_005_WB_3D_20170411\Chi_Xuemei_20170411_18711_005_PET_CT_3D_WB_WB_3D_92000.hdr',
                  r'F:\temp\Chi_Xuemei\18711_005_WB_3D_20170411\Chi_Xuemei_20170411_18711_005_PET_CT_3D_WB_WB_3D_184000.hdr',
                  r'F:\temp\Chi_Xuemei\18711_005_WB_3D_20170411\Chi_Xuemei_20170411_18711_005_PET_CT_3D_WB_WB_3D_277000.hdr',
                  r'F:\temp\Chi_Xuemei\18711_005_WB_3D_20170411\Chi_Xuemei_20170411_18711_005_PET_CT_3D_WB_WB_3D_369000.hdr',
                  r'F:\temp\Chi_Xuemei\18711_005_WB_3D_20170411\Chi_Xuemei_20170411_18711_005_PET_CT_3D_WB_WB_3D_462000.hdr',
                  r'F:\temp\Chi_Xuemei\18711_005_WB_3D_20170411\Chi_Xuemei_20170411_18711_005_PET_CT_3D_WB_WB_3D_554000.hdr',
                  ]
    for filename in population:
        transformixImageFilter.SetMovingImage(sitk.ReadImage(filename))
        transformixImageFilter.Execute()
        sitk.Show(transformixImageFilter.GetResultImage())


if __name__ == '__main__':
    transformParameterMap = get_registration_parameters()
    apply_registration_parameters(transformParameterMap)
