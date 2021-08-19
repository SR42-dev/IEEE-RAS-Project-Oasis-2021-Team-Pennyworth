import cv2
import numpy as np

user_color = input("type desired color: ")

file_location = 'InputVideo_ColorNotebooks.mp4'

cap = cv2.VideoCapture(file_location)
cap.set(3,1280)
cap.set(4,720)

font = cv2.FONT_HERSHEY_COMPLEX

ynb_lower = np.array([10,120,150]) #for yellow notebook
ynb_upper = np.array([90,255,255])

rnb_lower = np.array([0,115,145]) #for red notebook
rnb_upper = np.array([9,255,255])

gnb_lower = np.array([35,75,115]) #for green notebook
gnb_upper = np.array([55,255,255])

def getmask(hsvframe, colorchoice):
    if colorchoice == 'yellow':
        return cv2.inRange(hsvframe, ynb_lower, ynb_upper)
    elif colorchoice == 'red':
        return cv2.inRange(hsvframe, rnb_lower, rnb_upper)
    elif colorchoice == 'green':
        return cv2.inRange(hsvframe, gnb_lower, gnb_upper)

while True:
    ret, frame = cap.read()
    if not ret:
        print('video ended')
        break
    (h, w) = frame.shape[:2]
    blur = cv2.GaussianBlur(frame,(5,5),cv2.BORDER_DEFAULT)
    hsvvid = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    color_mask = getmask(hsvvid, user_color)
    color_contours, hierarchy = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(color_contours) != 0:
        sorted_color_contours = sorted(color_contours, key=cv2.contourArea, reverse= False)
        for color_contour in sorted_color_contours:
            x_color, y_color, w_color, h_color = cv2.boundingRect(color_contour)
            if w_color*h_color > 200000:
                cv2.rectangle(frame, (x_color, y_color), (x_color + w_color, y_color + h_color), (255, 0, 0), 3)
                print('colour detected')
                stop_text = 'colour detected'
                cv2.putText(frame, stop_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)
                break

    cv2.imshow('path video', frame)
    key = cv2.waitKey(50)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
