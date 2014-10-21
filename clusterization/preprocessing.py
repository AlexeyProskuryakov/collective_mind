# coding=utf-8
__author__ = '4ikist'

import numpy as np


# def get_data():
# """Возвращает списки идентификаторов объектов и матрицу значений"""
#     source = [row.strip().split(';') for row in file('products.csv')]
#     names = [row[0].decode('UTF-8') for row in source[1:]]
#     data = [map(float, row[1:]) for row in source[1:]]
#     return names, norm(data)


def norm(data, transpose=False):
    """Нормирование данных
    :param data матрица n x m из float
    :return нормированные данные [0,1]
    """
    matrix = np.array(data, 'f')
    len_val = len(matrix[1, :])
    for i in range(len_val):
        local_min = matrix[:, i].min()
        if local_min != 0.0:
            matrix[:, i] -= local_min
        local_max = matrix[:, i].max()
        if local_max != 0.0:
            matrix[:, i] /= local_max
    if transpose:
        matrix = matrix.T
    return matrix.tolist()