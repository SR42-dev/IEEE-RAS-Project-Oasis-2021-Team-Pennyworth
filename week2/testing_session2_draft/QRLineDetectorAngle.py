from pyzbar.pyzbar import decode
import cv2
import numpy as np
import math
import serial
import time

ser = serial.Serial('COM3', baudrate = 9600, timeout = 1)

def write_read(x):
    x = str(x)[2]
    ser.write(bytes(x, 'utf-8'))
    time.sleep(0.05)
    data = ser.readline()
    return data

def barcodeReader(image):
    img = image
    cv2.imshow("Image", img)

    detectedBarcodes = decode(img)

    if not detectedBarcodes:
        print("Barcode Not Detected or your barcode is blank/corrupted!")
        cv2.imshow("Image", img)
    else:

        for barcode in detectedBarcodes:

            (x, y, w, h) = barcode.rect

            cv2.rectangle(img, (x - 10, y - 10),
                          (x + w + 10, y + h + 10),
                          (0, 0, 255), 5)

            if barcode.data != " ":

                dir1 = barcode.data
                print(str(dir1)[2])

                while True:
                    value = write_read(dir1)
                    break

                cv2.imshow("Image", img)
    print(value)
    return value


cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)

#hsv lower and upper values for a yellow ball used for testing. Values found using trackbars.
path_lower = np.array([115,35,60])
path_upper = np.array([133,255,255])

font = cv2.FONT_HERSHEY_COMPLEX
kernel = np.ones((5,5),np.uint8)

skew_value = 15

f_dist = 200*3

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
    cv2.drawContours(frame, path_contours, -1, (0,255,0), 3)

    if len(path_contours) > 0:
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

        a_delay = (100/skew_value)*(ang + error_angle)
        a_delay = int(a_delay)
        #cv2.putText(frame, str(a_delay), (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)
        ser.write(str(a_delay).encode())

        if barcodeReader(frame) == '' : # edit string to contain qrcode data, case - switch to left track

            i = 'l' # edit to go to track on left
            ser.write(i.encode())
            print('go left')
            left_text = 'Go left'
            cv2.putText(frame, left_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(abs(a_delay) / 1000)

        elif barcodeReader(frame) == '' : # edit string to contain qrcode data, case - switch to right track

            i = 'r' # edit to go to track on right
            ser.write(i.encode())
            print('go right')
            left_text = 'Go right'
            cv2.putText(frame, left_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(abs(a_delay) / 1000)

        elif barcodeReader(frame) == '' : # edit string to contain qrcode data, case - go to center

            i = 'r'  # edit to go to center
            ser.write(i.encode())
            print('go right')
            left_text = 'Go right'
            cv2.putText(frame, left_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(abs(a_delay) / 1000)

        elif barcodeReader(frame) == '' : # edit string to contain qrcode data, case - stop

            i = ''  # edit to stop
            ser.write(i.encode())
            print('stop')
            left_text = 'stop'
            cv2.putText(frame, left_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(abs(a_delay) / 1000)

        elif a_delay < -20:
            i = 'l'
            ser.write(i.encode())
            print('go left')
            left_text = 'Go left'
            cv2.putText(frame, left_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(abs(a_delay)/1000)

        elif a_delay > 20:
            i = 'r'
            ser.write(i.encode())
            print('go right')
            right_text = 'Go right'
            cv2.putText(frame, right_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(abs(a_delay)/1000)


        else:
            i = 'f'
            ser.write(i.encode())
            print('go straight')
            straight_text = 'Go straight'
            cv2.putText(frame, straight_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(0.1)
    else:
        i = 'r'
        ser.write(i.encode())
        print('go right')
        straight_text = 'Go right'
        cv2.putText(frame, straight_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)
        time.sleep(0.1)

    cv2.imshow('path video', frame)
    key = cv2.waitKey(1)
    if key == 27: #press esc to exit
        break

cap.release()
cv2.destroyAllWindows()
