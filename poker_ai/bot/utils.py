import cv2
import pytesseract

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



def make_high_contrast(image):
    image = cv2.adaptiveThreshold(image, 255,
	cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 21, 10)

    return image


def is_color_in_image(image, color : tuple, debug = False):
    """_summary_

    Args:
        image (_type_): BGR image
        color (tuple): BGR color tuple
        debug (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    lower = (color[0] - 5, color[1] - 5, color[2] - 5)
    upper = (color[0] + 5, color[1] + 5, color[2] + 5)
    mask = cv2.inRange(image, lower, upper)
    if cv2.countNonZero(mask) > 0:
        return True
    else:
        return False

def crop_image_by_bbox(image, bbox):

    return image[bbox["top_left"][1]:bbox["bottom_left"][1], bbox["top_left"][0]:bbox["top_right"][0]]

def do_OCR(image, lang='eng'):
    text=pytesseract.image_to_string(image, lang=lang, config='--psm 11 -c tessedit_char_whitelist=,0123456789')
    text = text.replace("\n", "")
    return text

def get_play_order(dealer_index : int, num_players : int):

    if dealer_index+1 == num_players:
        order = [str(i) for i in range(0, num_players)]

    else:
        order = [str(i) for i in range(dealer_index+1, num_players)] + [str(i) for i in range(0, dealer_index+1)]
    
    return order