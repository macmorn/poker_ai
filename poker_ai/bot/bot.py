from distutils.log import debug
from re import template
import cv2
import pyautogui
import time
import numpy as np

if __name__ == "__main__":
    template=cv2.imread("poker_ai/bot/assets/dealer.png", 0)
    w, h = template.shape[::-1]
    threshold = 0.8
    while True:
        img=pyautogui.screenshot()
        img_rgb=cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)#this only visualizes
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where( result >= threshold)
        for pt in zip(*loc[::-1]):
            cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
        cv2.imshow('image', img_rgb)

        time.sleep(1)