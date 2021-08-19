# Ball following logic by bounding rectangle calculations

import cv2
import numpy as np
import serial

#######################################################################################################################
# Arduino communication
#######################################################################################################################

Arduino_Serial = serial.Serial('COM9',9600)  # (port, baud rate)

def write_read(x):
    x = str(x)
    Arduino_Serial.write(bytes(x, 'utf-8'))
    time.sleep(0.05)
    data = str(Arduino_Serial.readline())
    print(data)

#######################################################################################################################
# Ball detection
#######################################################################################################################
cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)

#hsv lower and upper values for blue pen ink that was used to make a rough path on a paper for testing. Values found using trackbars.
ball_lower = np.array([115,35,60])
ball_upper = np.array([133,255,255])

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

    ball_mask = cv2.inRange(hsvvid, ball_lower, ball_upper)
    opening = cv2.morphologyEx(ball_mask, cv2.MORPH_OPEN, kernel)
    erosion = cv2.erode(opening,kernel,iterations = 3)
    dilation = cv2.dilate(erosion,kernel,iterations = 5)
    ball_contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(ball_contours) != 0 :
        sorted_ball_contours = sorted(ball_contours, key=cv2.contourArea, reverse=False)
        if stop_variable == 0 :

            for ball_contour in sorted_ball_contours:
                x_barrier, y_barrier, w_barrier, h_barrier = cv2.boundingRect(ball_contour)
                path_centroid_x = x_barrier + (w_barrier / 2)
                path_centroid_y = y_barrier + (h_barrier / 2)

                if path_centroid_x < w/2 - 150:
                    print('go left')
                    for i in range(0, 1):  # change '1' for number of commands to be printed
                        write_read('l')
                    left_text = 'Go left'
                    cv2.putText(frame, left_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)

                elif path_centroid_x > w/2 + 150 :
                    print('go right')
                    for i in range(0, 1) : # change '1' for number of commands to be printed
                        write_read('r')
                    right_text = 'Go right'
                    cv2.putText(frame, right_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)

                else :
                    print('go straight')
                    for i in range(0, 1):  # change '1' for number of commands to be printed
                        write_read('f')
                    straight_text = 'Go straight'
                    cv2.putText(frame, straight_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)

        else:
            print('stop')
            for i in range(0, 1):  # change '1' for number of commands to be printed
                write_read('f')
            straight_text = 'Go straight'
            cv2.putText(frame, straight_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)

    else:
        print('go straight')
        for i in range(0, 1):  # change '1' for number of commands to be printed
            write_read('f')
        straight_text = 'Go straight'
        cv2.putText(frame, straight_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)

    cv2.imshow('path video', frame)
    key = cv2.waitKey(1)
    if key == 27: # press esc to exit
        break

cap.release()
cv2.destroyAllWindows()
