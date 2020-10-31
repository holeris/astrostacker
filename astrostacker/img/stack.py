import logging
import numpy as np
from astropy.io import fits as pyfits
from astrostacker.img.shift import shift
from astrostacker.img.debayer import debayer
from astrostacker.img.debayer import debayer2
from astrostacker.img.debayer import RGGB
import astroalign as aa

logger = logging.getLogger()


def stack(filenames, debayer_result=False, mask=RGGB, ref_frame_idx=0):
    logger.info(f'Stacking {len(filenames):d} files.')
    if ref_frame_idx >= len(filenames):
        ref_frame_idx = 0
    logger.info(f'Loading: {filenames[ref_frame_idx]:s}')
    img = pyfits.open(filenames[ref_frame_idx])
    result = img[0].data
    ref_frame = result.astype(np.int)
    img.close()
    logger.info(f'{filenames[0]:s} loaded. Set as reference image.')
    result = result.astype(np.int)
    remaining_files = list(range(0, len(filenames)))
    remaining_files.remove(ref_frame_idx)
    for i in remaining_files:
        filepath = filenames[i]
        filename = filepath[filepath.rfind('\\')+1:]
        logger.info(f'Loading {filename:s}')
        img = pyfits.open(filepath)
        data = img[0].data
        img.close()
        logger.info(f'{filename:s} loaded.')
        logger.info(f'Registering {filename:s}')
        trans = aa.find_transform(data, ref_frame)[0]
        rotation = int(trans.rotation)
        translation_x = int(trans.translation[0])
        translation_y = int(trans.translation[1])
        if rotation > 0:
            logger.info(f'Rotate: {rotation}')

        if abs(translation_x) > 1 or abs(translation_y > 1):
            logger.info(f'Move X={translation_x}, Y={translation_y}')
            data = shift(data, translation_x, translation_y)

        logger.info(f'{filename:s} registered.')
        registered_image = data
        result += registered_image.astype(np.int)
        logger.info(f'{filename:s} stacked.')
    n = len(filenames)
    result = result / n
    result = result.astype(np.uint16)
    if debayer_result:
        logger.info('Debayering stack.')
        # result = debayer(result)
        result = debayer2(result, mask)
        logger.info('Stack debayered.')
    return result
