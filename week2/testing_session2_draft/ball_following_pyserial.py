import cv2
import numpy as np
import serial
import time

ser = serial.Serial('COM3', baudrate = 9600, timeout = 1)

cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)

#hsv lower and upper values for a yellow ball used for testing. Values found using trackbars.
ball_lower = np.array([20,99,150])
ball_upper = np.array([90,255,255])

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
    erosion = cv2.erode(opening,kernel,iterations = 1)
    dilation = cv2.dilate(erosion,kernel,iterations = 5)
    ball_contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(ball_contours) > 0:
        largest = max(ball_contours, key = cv2.contourArea)
        #print(cv2.contourArea(largest))
        if cv2.contourArea(largest) < 25000:
            cnt_1 = largest
            M_1 = cv2.moments(cnt_1)
            ball_centroid_x = int(M_1['m10']/M_1['m00'])
            ball_centroid_y = int(M_1['m01'] / M_1['m00'])

            if ball_centroid_x < w/2 - 150:
                i = 'l'
                ser.write(i.encode())
                print('go left')
                left_text = 'Go left'
                cv2.putText(frame, left_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)

            elif ball_centroid_x > w/2 + 150:
                i = 'r'
                ser.write(i.encode())
                print('go right')
                right_text = 'Go right'
                cv2.putText(frame, right_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)

            else:
                i = 'f'
                ser.write(i.encode())
                print('go straight')
                straight_text = 'Go straight'
                cv2.putText(frame, straight_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)

        else:
            i = 'r'
            ser.write(i.encode())
            print('right')
            straight_text = 'right'
            cv2.putText(frame, straight_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)

    else:
        i = 's'
        ser.write(i.encode())
        print('stop')
        straight_text = 'stop'
        cv2.putText(frame, straight_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)

    time.sleep(0.175)
    cv2.imshow('ball video', frame)
    key = cv2.waitKey(1)
    if key == 27: #press esc to exit
        break

cap.release()
cv2.destroyAllWindows()
