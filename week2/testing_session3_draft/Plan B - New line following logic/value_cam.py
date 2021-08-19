import cv2
import numpy as np
import time

cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)

path_lower = np.array([0,80,0])
path_upper = np.array([179,255,255])

font = cv2.FONT_HERSHEY_COMPLEX
kernel = np.ones((5,5),np.uint8)

while True:
    ret, frame = cap.read()
    if not ret:
        cap = cv2.VideoCapture(0)
        continue
    (h, w) = frame.shape[:2]
    blur = cv2.GaussianBlur(frame,(5,5),cv2.BORDER_DEFAULT)
    hsvvid = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    path_mask = cv2.inRange(hsvvid, path_lower, path_upper)
    opening = cv2.morphologyEx(path_mask, cv2.MORPH_OPEN, kernel)
    erosion = cv2.erode(opening,kernel,iterations = 1)
    dilation = cv2.dilate(erosion,kernel,iterations = 5)
    path_contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(path_contours) > 0:
        largest = max(path_contours, key = cv2.contourArea)
        x_2, y_2, w_2, h_2 = cv2.boundingRect(largest)
        cv2.rectangle(frame, (x_2, y_2), (x_2 + w_2, y_2 + h_2), (0, 0, 255), 3)
        error_x = x_2 + (w_2/2) - w/2
        error_y = h/2 - y_2 + (h_2/2)
        cv2.putText(frame, str(error_y), (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, str(error_x), (5, 500), font, 2, (0, 0, 255), 2, cv2.LINE_AA)

    cv2.imshow('path video', frame)
    key = cv2.waitKey(1)
    if key == 27: #press esc to exit
        break

cap.release()
cv2.destroyAllWindows()
