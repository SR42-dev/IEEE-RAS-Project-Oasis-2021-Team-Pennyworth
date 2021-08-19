import cv2
import numpy as np
import serial
import time

ser = serial.Serial('/dev/ttyACM0', baudrate = 9600, timeout = 1)

cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)

path_lower = np.array([0,80,0])
path_upper = np.array([179,255,255])

black_upper = np.array([0,90,0]) # Black : switch to right track
black_lower = np.array([179,255,130])

violet_upper = np.array([120,120,0]) # Violet : switch to left track
violet_lower = np.array([140,255,255])

pink_upper = np.array([120,60,0]) # Pink : move to center of board and keep going till a line is reacquired
pink_lower = np.array([179,150,255])

font = cv2.FONT_HERSHEY_COMPLEX
kernel = np.ones((5,5),np.uint8)

f_dist = 2*400

while True:
    ret, frame = cap.read()
    if not ret:
        cap = cv2.VideoCapture(0)
        continue
    (h, w) = frame.shape[:2]
    blur = cv2.GaussianBlur(frame,(5,5),cv2.BORDER_DEFAULT)
    hsvvid = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    path_mask = cv2.inRange(hsvvid, path_lower, path_upper)
    black_mask = cv2.inRange(hsvvid, black_lower, black_upper)
    violet_mask = cv2.inRange(hsvvid, violet_lower, violet_upper)
    pink_mask = cv2.inRange(hsvvid, pink_lower, pink_upper)

    black_contours, hierarchy = cv2.findContours(black_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    violet_contours, hierarchy = cv2.findContours(violet_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    pink_contours, hierarchy = cv2.findContours(pink_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    opening = cv2.morphologyEx(path_mask, cv2.MORPH_OPEN, kernel)
    erosion = cv2.erode(opening,kernel,iterations = 1)
    dilation = cv2.dilate(erosion,kernel,iterations = 5)
    path_contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(black_contours) > 0 and cv2.contourArea(black_contour[0]) > 100:
        cv2.putText(frame, 'Switching tracks ...', (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)
        for a in range(26): # change range parameter according to test
            i = 'r'
            ser.write(i.encode())
            time.sleep(0.050)
        for a in range(6):
            i = 'f'
            ser.write(i.encode())
            time.sleep(0.175)
        for a in range(26):
            i = 'l'
            ser.write(i.encode())
            time.sleep(0.050)

    elif len(violet_contours) > 0 and cv2.contourArea(violet_contour[0]) > 100:
        cv2.putText(frame, 'Switching tracks ...', (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)
        for a in range(26): # change range parameter according to test
            i = 'l'
            ser.write(i.encode())
            time.sleep(0.050)
        for a in range(6):
            i = 'f'
            ser.write(i.encode())
            time.sleep(0.175)
        for a in range(26):
            i = 'r'
            ser.write(i.encode())
            time.sleep(0.050)

    elif len(pink_contours) > 0 and cv2.contourArea(pink_contour[0]) > 100:
        cv2.putText(frame, 'Moving to center', (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)
        for a in range(26): # change range parameter according to test
            i = 'l'
            ser.write(i.encode())
            time.sleep(0.050)
        for a in range(6):
            i = 'f'
            ser.write(i.encode())
            time.sleep(0.175)
        ser.write(i.encode())
        while len(path_contours) == 0:
            i = 'f'
            ser.write(i.encode())
            time.sleep(0.175)
        for a in range(26):
            i = 'l'
            ser.write(i.encode())
            time.sleep(0.175)

    elif len(path_contours) > 0:
        largest = max(path_contours, key = cv2.contourArea)
        x_2, y_2, w_2, h_2 = cv2.boundingRect(largest)
        cv2.rectangle(frame, (x_2, y_2), (x_2 + w_2, y_2 + h_2), (0, 0, 255), 3)
        error = x_2 + (w_2/2) - w/2
        #cv2.putText(frame, str(error), (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)

        blackbox = cv2.minAreaRect(largest)
        (x_min, y_min), (w_min, h_min), ang = blackbox
        if ang > 45:
            ang = ang - 90
        if w_min < h_min and ang < 0:
            ang = 90 + ang
        if w_min > h_min and ang > 0:
            ang = ang - 90
        ang = int(ang)
        box = cv2.boxPoints(blackbox)
        box = np.int0(box)
        cv2.drawContours(frame, [box], 0, (0,0,255), 3)
        #cv2.putText(frame, str(ang), (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)

        if error != 0:
            error_angle = abs((180/math.pi)*math.asin(abs(error)/f_dist)/error)*error
        else:
            error_angle = 0

        tot_angle = ang + error_angle

        if tot_angle < -10:
            i = 'l'
            ser.write(i.encode())
            print('go left')
            left_text = 'Go left'
            cv2.putText(frame, left_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(0.05)

        elif tot_angle > 10:
            i = 'r'
            ser.write(i.encode())
            print('go right')
            right_text = 'Go right'
            cv2.putText(frame, right_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(0.05)

        else:
            i = 'f'
            ser.write(i.encode())
            print('go straight')
            straight_text = 'Go straight'
            cv2.putText(frame, straight_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(0.175)

    else:
        i = 'r'
        ser.write(i.encode())
        print('looking for path')
        straight_text = 'looking for path'
        cv2.putText(frame, straight_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)
        time.sleep(0.05)

    cv2.imshow('path video', frame)
    key = cv2.waitKey(1)
    if key == 27: #press esc to exit
        break

cap.release()
cv2.destroyAllWindows()
