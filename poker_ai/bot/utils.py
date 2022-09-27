import cv2

def resize_image(image, scale_percent):
    width = int(image.shape[1] * scale_percent)
    height = int(image.shape[0] * scale_percent)
    dim = (width, height)

    return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)