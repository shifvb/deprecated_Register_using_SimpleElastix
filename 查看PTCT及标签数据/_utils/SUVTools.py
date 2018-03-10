import os
import natsort
import glob
import time

import numpy as np
import dicom
import datetime

ctPixscale = {}  # 关于CT图像的像素间距，属性包括    pixelSpacing：像素间间距   sliceThickness：切片厚度
ptPixscale = {}  # 关于PT图像的像素间距
baseInfo = {}  # 计算SUV值所必须的基本属性。一般调用getSUVs或者 getASUV时自动生成


def getBaseInfo():
    '''
    查看读入的切片基本信息
    :return: 返回基本信息字典，包含：
    ID，modality，weight，height，birthday，name，age，sex，
    lbm：瘦体重
    dose： 药物注射的剂量
    actualDose：放射剩余剂量
    medicineType： 药物种类 示踪剂名称
    sliceThickness ： 层间厚度
    pixelSpacing：  # tupel类型，两个元素一般相等，表示两个坐标轴上像素点之间对应的实际距离
    '''
    return baseInfo


def getCtPixscale():
    return ctPixscale


def getPtPixscale():
    return ptPixscale


def _read_dicom_series(directory, filepattern="PT_*"):
    '''
    读取dicom格式的图像
    :param directory: str PET图像序列存储文件夹
    :param filepattern: str 图像名正则
    :return: pixel_array像素数据 图像序列则返回三维数组，前两维为图像长宽，最后一维为切片索引维 slope像素值放缩
    '''

    if not os.path.exists(directory) or not os.path.isdir(directory):
        raise ValueError("Given directory does not exist or is a file : " + str(directory))
    # 生成文件夹下文件路径
    lstFilesDCM = natsort.natsorted(glob.glob(os.path.join(directory, filepattern)))
    # 从第一个文件中获取患者信息
    meta = dicom.read_file(lstFilesDCM[0])
    _genBaseInfo(meta)
    pixelArray = []
    slopes = []
    # 循环读取文件
    for filenameDCM in lstFilesDCM:
        # 获取每个文件信息
        ds = dicom.read_file(filenameDCM)
        # 保存原始像素数据
        pixelArray.append(ds.pixel_array)
        slopes.append(ds.get('RescaleSlope'))
    pixelArray = np.transpose(pixelArray, (1, 2, 0))
    slopes = np.array(slopes)
    return pixelArray, slopes


def _genPtscale(pixelSpacing, sliceThickness):
    '''
    生成pt的像素间距对象
    '''
    ptPixscale['pixelSpacing'] = pixelSpacing
    ptPixscale['sliceThickness'] = sliceThickness


def _genCtscale(pixelSpacing, sliceThickness):
    '''
    生成c的像素间距对象
    '''
    ctPixscale['pixelSpacing'] = pixelSpacing
    ctPixscale['sliceThickness'] = sliceThickness


def _genBaseInfo(meta):
    '''
    生成基本信息对象
    :param meta: dcm图像文件头
    :return: 将生成的对象保存在baseInfo中，可以通过getBaseInfo得到，此函数无返回值
    '''
    baseInfo['ID'] = meta.get('PatientID', None)
    baseInfo['modality'] = meta.get('Modality', None)  # 医学图像的模态，PET为'PT'，CT为'CT'
    baseInfo['weight'] = meta.get('PatientWeight', None)  # 体重单位为kg
    baseInfo['height'] = meta.get('PatientSize', None) * 100  # 身高换算为以厘米为单位
    baseInfo['birthday'] = meta.get('PatientBirthDate', None)
    baseInfo['name'] = meta.get('PatientName', None)
    age = meta.get('PatientAge', None)
    if None != age:
        baseInfo['age'] = age[:-1]  # 去掉后面的单位'Y'

    baseInfo['sex'] = meta.get('PatientSex', None)

    if baseInfo['sex'] == 'F':
        lbmKg = 1.07 * baseInfo['weight'] - 148 * (baseInfo['weight'] / baseInfo['height']) ** 2
    else:
        lbmKg = 1.10 * baseInfo['weight'] - 120 * (baseInfo['weight'] / baseInfo['height']) ** 2
    baseInfo['lbm'] = lbmKg

    # 示踪剂注射总剂量
    if None != meta.get('RadiopharmaceuticalInformationSequence'):
        tracerActivity = meta.get('RadiopharmaceuticalInformationSequence')[0].get('RadionuclideTotalDose')

        theDate = meta.get('SeriesDate')
        measureTime = meta.get('RadiopharmaceuticalInformationSequence')[0].get('RadiopharmaceuticalStartTime')
        measureTime = time.strptime(theDate + measureTime[0:6], '%Y%m%d%H%M%S')
        measureTime = datetime.datetime(*measureTime[:6])
        # scanTime=meta.get('SeriesDate')+meta.get('SeriesTime')
        scanTime = meta.get('SeriesTime')
        scanTime = time.strptime(theDate + scanTime, '%Y%m%d%H%M%S')
        scanTime = datetime.datetime(*scanTime[:6])
        halfTime = meta.get('RadiopharmaceuticalInformationSequence')[0].get('RadionuclideHalfLife')
        if (scanTime > measureTime):
            actualActivity = tracerActivity * (2) ** (-(scanTime - measureTime).seconds / halfTime)
        else:
            raise ('time wrong:scanTime should be later than measure')

        baseInfo['dose'] = tracerActivity  # 药物注射的剂量
        baseInfo['actualDose'] = actualActivity

    medicineType = meta.get((0x0009, 0x1036))  # 药物种类 (0x0009, 0x1036)是示踪剂名称：tracer_name对应的tag，非空时通过value得到它的值
    if None != medicineType:
        baseInfo['medicineType'] = medicineType.value
    else:
        baseInfo['medicineType'] = None
    baseInfo['sliceThickness'] = meta.get('SliceThickness', None)  # 层间厚度
    baseInfo['pixelSpacing'] = meta.get('PixelSpacing', None)  # tupel类型，两个元素一般相等，表示两个坐标轴上像素点之间对应的实际距离
    if meta.get('Modality', None) == 'CT':
        _genCtscale(meta.get('PixelSpacing', None), meta.get('SliceThickness', None))
    elif meta.get('Modality', None) == 'PT':
        _genPtscale(meta.get('PixelSpacing', None), meta.get('SliceThickness', None))


def getASuv(filePath):
    '''
    得到单张图像的SUV
    :param filePath:dcm文件路径
    :return: 以瘦体重标准计算的SUV值
    '''
    meta = dicom.read_file(filePath)
    pixel = meta.pixel_array
    slope = meta.get('RescaleSlope')
    _genBaseInfo(meta)
    suvLbm = pixel * slope * baseInfo['lbm'] * 1000 / baseInfo['actualDose']
    return suvLbm


def _calSuv(pixels, slopes):
    '''
    内部函数，计算SUV值
    :param pixels: 图像的像素点值矩阵
    :param slopes: 像素值放缩比，同一患者的不同切片间的slope可能会不一样
    :return: ndarray三维数组，表示SUV值，前两维为图像长宽，第三维为图像索引维
    '''
    lbmKg = baseInfo['lbm']  # 瘦体重
    actualActivity = baseInfo['actualDose']  # 示踪剂注射总剂量
    suvLbm = []
    for i in range(pixels.shape[2]):
        suvLbm.append(pixels[:, :, i] * slopes[i] * lbmKg * 1000 / actualActivity)
    return np.array(suvLbm)


def getSUVs(path, filepattern):
    '''
    计算给定路径下所有PET图像的SUV值
    :param path: PET图像序列的路径
    :return: numpy三维数组，表示一个人体各处的SUV值，前两维为图像长宽，最后一维为图像切片索引
    '''
    pixels, slopes = _read_dicom_series(path, filepattern)
    suvLbm = _calSuv(pixels, slopes)
    return suvLbm


def getRegistedSUVs(pixels, ptPath):
    pixels = pixels.transpose((1, 2, 0))  # 从register_image_series_pt2ct返回来的数组，第一维是索引维，_calSUV接受的数据第三维是索引维
    slopes = _read_slopes(ptPath)
    suvLbm = _calSuv(pixels, slopes)
    return suvLbm


def _read_slopes(directory, filepattern="PT_*"):
    if not os.path.exists(directory) or not os.path.isdir(directory):
        raise ValueError("Given directory does not exist or is a file : " + str(directory))
        # 生成文件夹下文件路径
    lstFilesDCM = natsort.natsorted(glob.glob(os.path.join(directory, filepattern)))
    # 从第一个文件中获取患者信息
    meta = dicom.read_file(lstFilesDCM[0])
    _genBaseInfo(meta)
    slopes = []
    # 循环读取文件
    for filenameDCM in lstFilesDCM:
        ds = dicom.read_file(filenameDCM)
        slopes.append(ds.get('RescaleSlope'))
    slopes = np.array(slopes)
    return slopes


def testBigSUV():
    ptp = r'D:\dataset\淋巴瘤3\迟学梅1\PT'
    ctp = r'D:\dataset\淋巴瘤3\迟学梅1\CT'
    return getRegistedSUVs(ctp, ptp)


if __name__ == '__main__':
    import pickle

    result = testBigSUV()
    with open(r'F:\dataset\淋巴瘤原始更多\淋巴瘤图像\t.pkl', 'wb') as f:
        pickle.dump(result, f)
