import numpy as np
from astrostacker.img.shift import shift

RGGB = 'rggb'
BGGR = 'bggr'
GBRG = 'gbrg'
GRBG = 'grbg'


def leftright(x):
    result = np.empty_like(x)
    x_left = shift(x, -1, 0)
    x_right = shift(x, 1, 0)
    tmp = [x_left, x_right]
    result = np.nanmean(tmp, axis=0, dtype=np.int)
    return result

def updown(x):
    result = np.empty_like(x)
    x_up = shift(x, 0, -1)
    x_down = shift(x, 0, 1)
    tmp = [x_up, x_down]
    result = np.nanmean(tmp, axis=0, dtype=np.int)
    return result


def x_shape(x):
    result = np.empty_like(x)
    x_left_up = shift(x, -1, -1)
    x_left_down = shift(x, -1, 1)
    x_right_up = shift(x, 1, -1)
    x_right_down = shift(x, 1, 1)
    tmp = [x_left_up, x_left_down, x_right_up, x_right_down]
    result = np.nanmean(tmp, axis=0, dtype=np.int)
    return result


def cross_shape(x):
    result = np.empty_like(x)
    x_left = shift(x, -1, 0)
    x_right = shift(x, 1, 0)
    x_up = shift(x, 0, -1)
    x_down = shift(x, 0, 1)
    tmp = [x_left, x_right, x_up, x_down]
    result = np.nanmean(tmp, axis=0, dtype=np.int)
    return result


def debayer(img, mask):
    # Bayer mask shape:
    # ---------
    # | P1 | P2 |
    # ---------
    # | P3 | P4 |
    # ---------
    mask = mask.lower()
    if mask == RGGB:
        mask_r = np.zeros(img.shape, dtype=np.int)
        mask_r[::2, ::2] = 1
        mask_g = np.zeros(img.shape, dtype=np.int)
        mask_g[::2, 1::2] = 1
        mask_g[1::2, ::2] = 1
        mask_b = np.zeros(img.shape, dtype=np.int)
        mask_b[1::2, 1::2] = 1
    elif mask == BGGR:
        mask_r = np.zeros(img.shape, dtype=np.int)
        mask_r[1::2, 1::2] = 1
        mask_g = np.zeros(img.shape, dtype=np.int)
        mask_g[::2, 1::2] = 1
        mask_g[1::2, ::2] = 1
        mask_b = np.zeros(img.shape, dtype=np.int)
        mask_b[::2, ::2] = 1
    elif mask == GBRG:
        mask_r = np.zeros(img.shape, dtype=np.int)
        mask_r[1::2, ::2] = 1
        mask_g = np.zeros(img.shape, dtype=np.int)
        mask_g[::2, ::2] = 1
        mask_g[1::2, 1::2] = 1
        mask_b = np.zeros(img.shape, dtype=np.int)
        mask_b[::2, 1::2] = 1
    elif mask == GRBG:
        mask_r = np.zeros(img.shape, dtype=np.int)
        mask_r[::2, 1::2] = 1
        mask_g = np.zeros(img.shape, dtype=np.int)
        mask_g[::2, ::2] = 1
        mask_g[1::2, 1::2] = 1
        mask_b = np.zeros(img.shape, dtype=np.int)
        mask_b[1::2, ::2] = 1
    else:
        raise Exception('Not supported bayer mask format.')

    r = img * mask_r
    g = img * mask_g
    b = img * mask_b

    mask_r = None
    mask_g = None
    mask_b = None

    r_leftright = leftright(r)
    r_updown = updown(r)
    r_x_shape = x_shape(r)

    g_cross_shape = cross_shape(g)

    b_leftright = leftright(b)
    b_updown = updown(b)
    b_x_shape = x_shape(b)

    r_for_p1 = debayer_r_for_p1(r, leftright=r_leftright, updown=r_updown, x_shape=r_x_shape, mask=mask)
    r_for_p2 = debayer_r_for_p2(r, leftright=r_leftright, updown=r_updown, x_shape=r_x_shape, mask=mask)
    r_for_p3 = debayer_r_for_p3(r, leftright=r_leftright, updown=r_updown, x_shape=r_x_shape, mask=mask)
    r_for_p4 = debayer_r_for_p4(r, leftright=r_leftright, updown=r_updown, x_shape=r_x_shape, mask=mask)
    r_new = r_for_p1 + r_for_p2 + r_for_p3 + r_for_p4

    g_for_p1_p3 = debayer_g_for_p1_p3(g, cross_shape=g_cross_shape, mask=mask)
    g_for_p2_p4 = debayer_g_for_p2_p4(g, cross_shape=g_cross_shape, mask=mask)
    g_new = g_for_p1_p3 + g_for_p2_p4

    b_for_p1 = debayer_b_for_p1(b, leftright=b_leftright, updown=b_updown, x_shape=b_x_shape, mask=mask)
    b_for_p2 = debayer_b_for_p2(b, leftright=b_leftright, updown=b_updown, x_shape=b_x_shape, mask=mask)
    b_for_p3 = debayer_b_for_p3(b, leftright=b_leftright, updown=b_updown, x_shape=b_x_shape, mask=mask)
    b_for_p4 = debayer_b_for_p4(b, leftright=b_leftright, updown=b_updown, x_shape=b_x_shape, mask=mask)
    b_new = b_for_p1 + b_for_p2 + b_for_p3 + b_for_p4

    result = np.stack((r_new, g_new, b_new), axis=2)
    return result


def debayer_r_for_p1(x, leftright, updown, x_shape, mask):
    if mask == RGGB:
        result = x
    elif mask == BGGR:
        result = x_shape
    elif mask == GBRG:
        result = updown
    elif mask == GRBG:
        result = leftright
    else:
        raise Exception('Not supported bayer mask format.')
    return result

def debayer_r_for_p2(x, leftright, updown, x_shape, mask):
    if mask == RGGB:
        result = leftright
    elif mask == BGGR:
        result = updown
    elif mask == GBRG:
        result = x_shape
    elif mask == GRBG:
        result = x
    else:
        raise Exception('Not supported bayer mask format.')
    return result

def debayer_r_for_p3(x, leftright, updown, x_shape, mask):
    if mask == RGGB:
        result = updown
    elif mask == BGGR:
        result = leftright
    elif mask == GBRG:
        result = x
    elif mask == GRBG:
        result = x_shape
    else:
        raise Exception('Not supported bayer mask format.')
    return result

def debayer_r_for_p4(x, leftright, updown, x_shape, mask):
    if mask == RGGB:
        result = x_shape
    elif mask == BGGR:
        result = x
    elif mask == GBRG:
        result = leftright
    elif mask == GRBG:
        result = updown
    else:
        raise Exception('Not supported bayer mask format.')
    return result

def debayer_g_for_p1_p3(x, cross_shape, mask):
    if mask == RGGB:
        result = cross_shape
    elif mask == BGGR:
        result = cross_shape
    elif mask == GBRG:
        result = x
    elif mask == GRBG:
        result = x
    else:
        raise Exception('Not supported bayer mask format.')
    return result

def debayer_g_for_p2_p4(x, cross_shape, mask):
    if mask == RGGB:
        result = x
    elif mask == BGGR:
        result = x
    elif mask == GBRG:
        result = cross_shape
    elif mask == GRBG:
        result = cross_shape
    else:
        raise Exception('Not supported bayer mask format.')
    return result

def debayer_b_for_p1(x, leftright, updown, x_shape, mask):
    if mask == RGGB:
        result = x_shape
    elif mask == BGGR:
        result = x
    elif mask == GBRG:
        result = leftright
    elif mask == GRBG:
        result = updown
    else:
        raise Exception('Not supported bayer mask format.')
    return result

def debayer_b_for_p2(x, leftright, updown, x_shape, mask):
    if mask == RGGB:
        result = updown
    elif mask == BGGR:
        result = leftright
    elif mask == GBRG:
        result = x
    elif mask == GRBG:
        result = x_shape
    else:
        raise Exception('Not supported bayer mask format.')
    return result

def debayer_b_for_p3(x, leftright, updown, x_shape, mask):
    if mask == RGGB:
        result = leftright
    elif mask == BGGR:
        result = updown
    elif mask == GBRG:
        result = x_shape
    elif mask == GRBG:
        result = x
    else:
        raise Exception('Not supported bayer mask format.')
    return result

def debayer_b_for_p4(x, leftright, updown, x_shape, mask):
    if mask == RGGB:
        result = x
    elif mask == BGGR:
        result = x_shape
    elif mask == GBRG:
        result = updown
    elif mask == GRBG:
        result = leftright
    else:
        raise Exception('Not supported bayer mask format.')
    return result
