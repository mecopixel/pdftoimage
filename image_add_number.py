import cv2
import numpy as np

number = 1

def draw_circle(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(imr,(x,y),100,(0,255,0),-1)

def draw_number(event,x,y,flags,param):
    global number
    if event == cv2.EVENT_LBUTTONDBLCLK:
        cv2.putText(imr,str(number),(x,y),cv2.FONT_HERSHEY_SIMPLEX,1.0,(0,0,255),2,cv2.LINE_4)
        number += 1

img = cv2.imread('./image_file/05B31365A1 MTL-XPS-PLATE_01.jpeg')

height = img.shape[0]
width = img.shape[1]

cv2.namedWindow(winname='mouse_drawing')

cv2.setMouseCallback('mouse_drawing',draw_number)

while True:
    cv2.imshow('mouse_drawing',imr)
    if cv2.waitKey(20) & 0xFF == 27:
        break

cv2.destroyAllWindows()