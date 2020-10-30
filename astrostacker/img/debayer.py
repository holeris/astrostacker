import numpy as np
from astrostacker.img.shift import shift


def debayer_g_for_r(x):
    result = np.empty_like(x)
    x_left = shift(x, -1, 0)
    x_right = shift(x, 1, 0)
    x_up = shift(x, 0, -1)
    x_down = shift(x, 0, 1)
    tmp = [x_left, x_right, x_up, x_down]
    result = np.nanmean(tmp, axis=0, dtype=np.int)
    result[1::2, 1::2] = 0
    return result


def debayer_b_for_r(x):
    result = np.empty_like(x)
    x_left_up = shift(x, -1, -1)
    x_left_down = shift(x, -1, 1)
    x_right_up = shift(x, 1, -1)
    x_right_down = shift(x, 1, 1)
    tmp = [x_left_up, x_left_down, x_right_up, x_right_down]
    result = np.nanmean(tmp, axis=0, dtype=np.int)
    return result


def debayer_r_for_g1(x):
    result = np.empty_like(x)
    x_left = shift(x, -1, 0)
    x_right = shift(x, 1, 0)
    tmp = [x_left, x_right]
    result = np.nanmean(tmp, axis=0, dtype=np.int)
    return result


def debayer_b_for_g1(x):
    result = np.empty_like(x)
    x_up = shift(x, 0, -1)
    x_down = shift(x, 0, 1)
    tmp = [x_up, x_down]
    result = np.nanmean(tmp, axis=0, dtype=np.int)
    return result


def debayer_r_for_g2(x):
    result = np.empty_like(x)
    x_up = shift(x, 0, -1)
    x_down = shift(x, 0, 1)
    tmp = [x_up, x_down]
    result = np.nanmean(tmp, axis=0, dtype=np.int)
    return result


def debayer_b_for_g2(x):
    result = np.empty_like(x)
    x_left = shift(x, -1, 0)
    x_right = shift(x, 1, 0)
    tmp = [x_left, x_right]
    result = np.nanmean(tmp, axis=0, dtype=np.int)
    return result


def debayer_r_for_b(x):
    result = np.empty_like(x)
    x_left_up = shift(x, -1, -1)
    x_left_down = shift(x, -1, 1)
    x_right_up = shift(x, 1, -1)
    x_right_down = shift(x, 1, 1)
    tmp = [x_left_up, x_left_down, x_right_up, x_right_down]
    result = np.nanmean(tmp, axis=0, dtype=np.int)
    return result


def debayer_g_for_b(x):
    result = np.empty_like(x)
    x_left = shift(x, -1, 0)
    x_right = shift(x, 1, 0)
    x_up = shift(x, 0, -1)
    x_down = shift(x, 0, 1)
    tmp = [x_left, x_right, x_up, x_down]
    result = np.nanmean(tmp, axis=0, dtype=np.int)
    result[0::2, 0::2] = 0
    return result


def debayer(img):
    # Bayer mask shape:
    # ---------
    # | R | G |
    # ---------
    # | G | B |
    # ---------
    mask_r = np.zeros(img.shape, dtype=np.int)
    mask_r[::2, ::2] = 1

    mask_g = np.zeros(img.shape, dtype=np.int)
    mask_g[::2, 1::2] = 1
    mask_g[1::2, ::2] = 1

    mask_b = np.zeros(img.shape, dtype=np.int)
    mask_b[1::2, 1::2] = 1

    r = img * mask_r
    g = img * mask_g
    b = img * mask_b

    b_for_g1 = debayer_r_for_g1(r)
    b_for_g2 = debayer_r_for_g2(r)
    r_for_b = debayer_r_for_b(r)
    r_new = r + b_for_g1 + b_for_g2 + r_for_b

    g_for_r = debayer_g_for_r(g)
    g_for_b = debayer_g_for_b(g)
    g_new = g + g_for_r + g_for_b

    b_for_r = debayer_b_for_r(b)
    b_for_g1 = debayer_b_for_g1(b)
    b_for_g2 = debayer_b_for_g2(b)
    b_new = b + b_for_r + b_for_g1 + b_for_g2

    result = np.stack((r_new, g_new, b_new), axis=2)
    return result
