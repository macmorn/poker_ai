import cv2
import pytesseract
from pyclick import HumanClicker
import time
import numpy as np

def resize_image(image, scale_percent):
    width = int(image.shape[1] * scale_percent)
    height = int(image.shape[0] * scale_percent)
    dim = (width, height)

    return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

def rotate_image_by_angle(image, angle):
    (h, w) = image.shape[:2]
    center = (w / 2, h / 2)
    M = cv2.getRotationMatrix2D(center, -angle, 1.0)
    img=cv2.warpAffine(image, M, (w, h))
    return img

def match_over_threshold(image, template, threshold, debug = False):

    if debug:
        for algorithm in [cv2.TM_CCOEFF, cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR, cv2.TM_CCORR_NORMED, cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            res=cv2.matchTemplate(image, template, algorithm)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            print(f"{algorithm} got {max_val}")

        res=cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        return max_val > threshold

    else:
        res=cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        return max_val > threshold



def make_high_contrast(image, adaptive= True, cutoff= 190):
    if adaptive:
        image = cv2.adaptiveThreshold(image, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 21, 10)
    else:
        ret, image = cv2.threshold(image, cutoff, 255, cv2.THRESH_BINARY)
    return image


def is_color_in_image(image, color : tuple, exact= False):
    """_summary_

    Args:
        image (_type_): BGR image
        color (tuple): BGR color tuple
        debug (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    if exact:
        mask = cv2.inRange(image, color, color)
    else:
        lower = (color[0] - 5, color[1] - 5, color[2] - 5)
        upper = (color[0] + 5, color[1] + 5, color[2] + 5)
        #make sure never go below 0
        if any([x < 0 for x in lower]):
            lower = (0,0,0)
        mask = cv2.inRange(image, lower, upper)
    if cv2.countNonZero(mask) > 0:
        return True
    else:
        return False

def crop_image_by_bbox(image, bbox):

    return image[bbox["top_left"][1]:bbox["bottom_left"][1], bbox["top_left"][0]:bbox["top_right"][0]]

def do_OCR(image, lang='eng', psm=11, debug=False):
    pytesseract.pytesseract.tesseract_cmd="/usr/local/Cellar/tesseract/4.1.1/bin/tesseract"
    text=pytesseract.image_to_string(image, lang=lang, config=f'--psm {psm} -c tessedit_char_whitelist=,.0123456789$')
    text = text.replace("\n", "")
    text = text.replace ("\x0c", "")
    if debug:
        cv2.imwrite(f"debug/ocr/bet_{text}_{time.time()}.png", image)
    return text

def draw_bb_with_coordinates(image , bb : dict, text : str = None):
    """Helper function to draw bounding box on screenshot.
    For debugging purposes.

    Args:
        bb (dict): bounding box dict
    """
    cv2.rectangle(image, bb["top_left"], bb["bottom_right"], 255, 2)
    if text:
        cv2.putText(image, text, bb["top_left"], cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255, 2)

    return image

def human_cursor_click(x, y, duration = 0.5):
    """_summary_

    Args:
        x (_type_): _description_
        y (_type_): _description_
        duration (float, optional): _description_. Defaults to 0.5.
    """
    hc = HumanClicker()
    hc.move((x,y),duration)
    hc.click()

def preprocess_for_ocr(image):
    #remove bg
    cv2.floodFill(image, None, (1,1), 0)
    cv2.floodFill(image, None, (image.shape[1]-1,image.shape[0]-1), 0)
    #add border and resize 4x
    image = cv2.copyMakeBorder(image, 20, 20, 5, 5, cv2.BORDER_CONSTANT)
    image=cv2.resize(image, (0, 0), fx=4, fy=4)
    #sharpen
    #kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    #image = cv2.filter2D(image, -1, kernel)
    #erode
    kernel = np.ones((3, 3), np.uint8)
    image = cv2.erode(image, kernel)
    #invert
    image = cv2.bitwise_not(image)
    return image