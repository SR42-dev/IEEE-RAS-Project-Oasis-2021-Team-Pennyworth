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

green_upper = np.array([88,162,154]) # Green : switch to right track
green_lower = np.array([68,142,74])

violet_upper = np.array([140,140,150]) # Violet : switch to left track
violet_lower = np.array([120,105,95])

pink_upper = np.array([179,120,255]) # Pink : move to center of board and keep going till a line is reacquired
pink_lower = np.array([150,53,150])

font = cv2.FONT_HERSHEY_COMPLEX
kernel = np.ones((5,5),np.uint8)

color_count = 0
path_num = 1

while True:
    ret, frame = cap.read()
    if not ret:
        cap = cv2.VideoCapture(0)
        continue
    (h, w) = frame.shape[:2]
    blur = cv2.GaussianBlur(frame,(5,5),cv2.BORDER_DEFAULT)
    hsvvid = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    path_mask = cv2.inRange(hsvvid, path_lower, path_upper)
    green_mask = cv2.inRange(hsvvid, green_lower, green_upper)
    violet_mask = cv2.inRange(hsvvid, violet_lower, violet_upper)
    pink_mask = cv2.inRange(hsvvid, pink_lower, pink_upper)

    green_contours, hierarchy = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    violet_contours, hierarchy = cv2.findContours(violet_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    pink_contours, hierarchy = cv2.findContours(pink_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    opening = cv2.morphologyEx(path_mask, cv2.MORPH_OPEN, kernel)
    erosion = cv2.erode(opening,kernel,iterations = 1)
    dilation = cv2.dilate(erosion,kernel,iterations = 5)
    path_contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if color_count == 0 and len(green_contours) > 0 : # Green check

        colour_count += 1
        path_num = 2
        cv2.putText(frame, 'Switching tracks ...', (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)

        for a in range(26): # change range parameter according to test, 0 if no turns
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

        continue

    elif color_count == 1 and len(violet_contours) > 0 : # Violet check

        colour_count += 1
        path_num = 1
        cv2.putText(frame, 'Switching tracks ...', (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)

        for a in range(26): # change range parameter according to test, 0 if no turns
            i = 'l'
            ser.write(i.encode())
            time.sleep(0.050)

        for a in range(6):
            i = 'f'
            ser.write(i.encode())
            time.sleep(0.110)

        for a in range(26):
            i = 'r'
            ser.write(i.encode())
            time.sleep(0.050)

        continue

    elif color_count == 2 and len(pink_contours) > 0 : # pink check

        colour_count += 1
        cv2.putText(frame, 'Moving across center', (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)

        for a in range(26): # change range parameter according to test, 0 if no turns
            i = 'l'
            ser.write(i.encode())
            time.sleep(0.050)
        for a in range(6):
            i = 'f'
            ser.write(i.encode())
            time.sleep(0.175)

        while len(path_contours) == 0:
            i = 'f'
            ser.write(i.encode())
            time.sleep(0.175)

        for a in range(26):
            i = 'l'
            ser.write(i.encode())
            time.sleep(0.175)

        continue

    elif len(path_contours) > 0:
        largest = max(path_contours, key = cv2.contourArea)
        M_1 = cv2.moments(largest)
        path_centroid_x = int(M_1['m10']/M_1['m00'])
        path_centroid_y = int(M_1['m01'] / M_1['m00'])

        if path_centroid_x < w/2 - 150:
            i = 'l'
            ser.write(i.encode())
            print('go left')
            left_text = 'Go left'
            cv2.putText(frame, left_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(0.05)

        elif path_centroid_x > w/2 + 150:
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
            time.sleep(0.110)

    else:

        if path_num == 1 :
            i = 'l'
        elif path_num == 2 :
            i = 'r'

        ser.write(i.encode())
        print('looking for path')
        straight_text = 'looking for path'
        cv2.putText(frame, straight_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)
        time.sleep(0.05)

    cv2.imshow('path video', frame)
    cv2.imshow('Green mask', green_mask)
    #cv2.imshow('Violet mask', violet_mask)
    #cv2.imshow('Pink mask', pink_mask)

    key = cv2.waitKey(1)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
