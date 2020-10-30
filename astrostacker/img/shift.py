import numpy as np


def shift_left_right(arr, offset, fill_value=0):
    result = np.empty_like(arr)
    if offset > 0:
        result[:, offset:] = arr[:, :-offset]
        result[:, :offset] = fill_value
    elif offset < 0:
        result[:, :offset] = arr[:, -offset:]
        result[:, offset:] = fill_value
    else:
        result = arr
    return result


def shift_up_down(arr, offset, fill_value=0):
    result = np.empty_like(arr)
    if offset < 0:
        result[:offset, :] = arr[-offset:, :]
        result[offset:, :] = fill_value
    elif offset > 0:
        result[offset:, :] = arr[:-offset, :]
        result[:offset, :] = fill_value
    else:
        result = arr
    return result


def shift(arr, left_right, up_down, fill_value=0):
    if left_right == 0 and up_down == 0:
        return arr
    result = shift_left_right(arr, left_right, fill_value)
    result = shift_up_down(result, up_down, fill_value)
    return result
