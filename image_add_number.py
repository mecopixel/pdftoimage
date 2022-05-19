import cv2

number = 1
multiple = 0.4

def draw_circle(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(img,(x,y),100,(0,255,0),-1)

def draw_number(event,x,y,flags,param):
    global number
    if event == cv2.EVENT_LBUTTONDBLCLK:
        cv2.putText(img,str(number),(x,y),cv2.FONT_HERSHEY_SIMPLEX,1.0,(0,0,255),2,cv2.LINE_4)
        number += 1

img = cv2.imread('./image_file/05B31365A1 MTL-XPS-PLATE_01.jpeg')

height = img.shape[0]
width = img.shape[1]

img = cv2.resize(img , (int(width * multiple), int(height * multiple)))
cv2.namedWindow("img", cv2.WINDOW_NORMAL)
cv2.namedWindow(winname='mouse_drawing')

cv2.setMouseCallback('mouse_drawing',draw_number)

while True:
    cv2.imshow('mouse_drawing',img)
    if cv2.waitKey(20) & 0xFF == 27:
        break

cv2.destroyAllWindows()