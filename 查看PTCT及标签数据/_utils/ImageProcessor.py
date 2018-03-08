import numpy as np
import dicom
import time
import datetime


def threshold_image(arr: np.ndarray, threshold: float):
    """
    将一个numpy数组形式的图像阈值化，并归一化
    :param arr: 要处理的numpy数组
    :param threshold: 阈值
    :return: 阈值化并归一化的， numpy array形式的图像
    """
    # 计算并存储阈值化图像
    _mask = np.array(arr > threshold, dtype=np.uint8)
    _arr = arr * _mask  # SUV < 2.0 的全部置为0
    if not _arr.min() == _arr.max():  # 归一化
        _arr = (_arr - _arr.min()) / (_arr.max() - _arr.min()) * 255  # 最大值等于最小值，正常归一化
    return np.array(_arr, dtype=np.uint8)  # 改变类型 np.float64 -> np.uint8


def norm_image(arr: np.ndarray):
    """
    将一个numpy数组正则化（0~255）,并转成np.uint8类型
    :param arr: 要处理的numpy数组
    :return: 值域在0~255之间的uint8数组
    """
    if not arr.min() == arr.max():
        arr = (arr - arr.min()) / (arr.max() - arr.min()) * 255
    return np.array(arr, dtype=np.uint8)


def cal_Hu(arr: np.ndarray, slope, intercept):
    """
    计算Hu值
    :param arr: CT原始值(uint16, range from 0 to 4096)
    :param slope: rescale scope (0028|1053)
    :param intercept: rescale intercept (0028|1052)
    :return: Hu值数组
    """
    return arr * slope + intercept


def cal_SUV(filePath: str):
    meta = dicom.read_file(filePath)
    pixel = meta.pixel_array
    slope = meta.get('RescaleSlope')
    weightKg = meta.get('PatientWeight')
    # 患者身高
    heightCm = meta.get('PatientSize') * 100  # 身高以厘米为单位
    # 患者性别
    sex = meta.get("PatientSex")
    # 示踪剂注射总剂量
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

    if sex == 'F':
        lbmKg = 1.07 * weightKg - 148 * (weightKg / heightCm) ** 2
    else:
        lbmKg = 1.10 * weightKg - 120 * (weightKg / heightCm) ** 2

    suvLbm = pixel * slope * lbmKg * 1000 / actualActivity
    # suv=np.uint8(suvLbm)

    return suvLbm
