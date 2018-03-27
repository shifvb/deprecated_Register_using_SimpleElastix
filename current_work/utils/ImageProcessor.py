import numpy as np


def gen_fuse_arr(base_arr: np.ndarray, fuse_arr: np.ndarray):
    """base数组保持白色，fuse数组为红色，融合后产生RGB数组"""
    return np.stack((base_arr / 2 + fuse_arr / 2, base_arr / 2, base_arr / 2)).transpose([1, 2, 0]).astype(np.uint8)


def threshold_image(arr: np.ndarray, threshold: float):
    """
    将一个numpy数组形式的图像阈值化，并归一化
    :param arr: 要处理的numpy数组
    :param threshold: 阈值
    :return: 阈值化并归一化的， numpy array形式的图像
    """
    # 计算并存储阈值化图像
    _mask = np.array(arr > threshold, dtype=np.uint8)
    _arr = arr * _mask  # SUV < threshold 的全部置为0
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


if __name__ == '__main__':
    arr = np.array([1, 3, 4])
    arr2 = threshold_image(arr, 3)
    print(arr)
    print(arr2)
    arr[0] = 1333
    print(arr)
    print(arr2)
