import cv2
import numpy as np
import serial
import time

def empty(a):  # argument required
    pass

ser = serial.Serial('/dev/ttyACM0', baudrate = 9600, timeout = 1)

cap = cv2.VideoCapture(0)
cap.set(3,360)
cap.set(4,480)

cv2.namedWindow('Trackbars')  # Creating trackbars to isolate required color
cv2.resizeWindow('Trackbars', 640, 280)

# cv2.createTrackbar('H minimum', 'Trackbars', 0, 179, empty) # 180 hues available in opencv (lower and upper limits for trackbars), empty is a function called each time the trackbar is changed
# cv2.createTrackbar('H maximum', 'Trackbars', 179, 179, empty) # initial trackbars for color detection and limit identification
# cv2.createTrackbar('S minimum', 'Trackbars', 0, 255, empty)
# cv2.createTrackbar('S maximum', 'Trackbars', 255, 255, empty)
# cv2.createTrackbar('V minimum', 'Trackbars', 0, 255, empty)
# cv2.createTrackbar('V maximum', 'Trackbars', 255, 255, empty)

cv2.createTrackbar('H minimum', 'Trackbars', 29, 179, empty)  # trackbars for specific colour
cv2.createTrackbar('H maximum', 'Trackbars', 146, 179, empty)
cv2.createTrackbar('S minimum', 'Trackbars', 13, 255, empty)
cv2.createTrackbar('S maximum', 'Trackbars', 93, 255, empty)
cv2.createTrackbar('V minimum', 'Trackbars', 66, 255, empty)
cv2.createTrackbar('V maximum', 'Trackbars', 127, 255, empty)

while True:

    ret, img = cap.read()
    if not ret:
        cap = cv2.VideoCapture(0)

    i = input("command: ")

    if i == 'f':
        ser.write(i.encode())
        time.sleep(0.175)
    elif i == 'l':
        ser.write(i.encode())
        time.sleep(0.05)
    elif i == 'r':
        ser.write(i.encode())
        time.sleep(0.05)
    elif i == 'b':
        ser.write(i.encode())
        time.sleep(0.175)

    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # conversion to HSV from BGR

    hMin = cv2.getTrackbarPos('H minimum', 'Trackbars')
    hMax = cv2.getTrackbarPos('H maximum', 'Trackbars')
    sMin = cv2.getTrackbarPos('S minimum', 'Trackbars')
    sMax = cv2.getTrackbarPos('S maximum', 'Trackbars')
    vMin = cv2.getTrackbarPos('V minimum', 'Trackbars')
    vMax = cv2.getTrackbarPos('V maximum', 'Trackbars')
    # print(hMin, hMax, sMin, sMax, vMin, vMax)

    lower = np.array([hMin, sMin, vMin])  # minimum range array
    upper = np.array([hMax, sMax, vMax])  # maximum range array
    mask = cv2.inRange(imgHSV, lower, upper)  # filtering out colours from HSV image
    imgResult = cv2.bitwise_and(img, img,mask=mask)  # adds two images and creates a new one where non black colours on the mask are given colour from the original

    # cv2.imshow('Original', img)
    # cv2.imshow('HSV', imgHSV)
    # cv2.imshow('Mask', mask)
    cv2.imshow('Result', imgResult)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

print(hMin, hMax, sMin, sMax, vMin, vMax)
cap.release()
cv2.destroyAllWindows()

