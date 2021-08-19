import cv2
import numpy as np

cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)

#hsv lower and upper values for blue pen ink that was used to make a rough path on a paper for testing. Values found using trackbars.
path_lower = np.array([115,35,60])
path_upper = np.array([133,255,255])

font = cv2.FONT_HERSHEY_COMPLEX
kernel = np.ones((5,5),np.uint8)

while True:
    ret, frame = cap.read()
    if not ret:
        cap = cv2.VideoCapture(file_location)
        continue
    (h, w) = frame.shape[:2]
    blur = cv2.GaussianBlur(frame,(5,5),cv2.BORDER_DEFAULT)
    hsvvid = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    path_mask = cv2.inRange(hsvvid, path_lower, path_upper)
    opening = cv2.morphologyEx(path_mask, cv2.MORPH_OPEN, kernel)
    erosion = cv2.erode(opening,kernel,iterations = 3)
    dilation = cv2.dilate(erosion,kernel,iterations = 5)
    path_contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(path_contours) > 1:
        sorted_path_contours= sorted(path_contours, key=cv2.contourArea, reverse= False)
        if cv2.contourArea(sorted_path_contours[0]) > 300 or cv2.contourArea(sorted_path_contours[1]) > 300:
            cnt_1 = sorted_path_contours[0]
            M_1 = cv2.moments(cnt_1)
            Cx_1 = int(M_1['m10']/M_1['m00'])
            Cy_1 = int(M_1['m01'] / M_1['m00'])
            cnt_2 = sorted_path_contours[1]
            M_2 = cv2.moments(cnt_2)
            Cx_2 = int(M_2['m10']/M_2['m00'])
            Cy_2 = int(M_2['m01'] / M_2['m00'])
            path_centroid_x = (Cx_1 + Cx_2)/2
            path_centroid_y = (Cy_1 + Cy_2)/2

            if path_centroid_x < w/2 - 150:
                print('go left')
                left_text = 'Go left'
                cv2.putText(frame, left_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)

            elif path_centroid_x > w/2 + 150:
                print('go right')
                right_text = 'Go right'
                cv2.putText(frame, right_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)

            else:
                print('go straight')
                straight_text = 'Go straight'
                cv2.putText(frame, straight_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)

        else:
            print('go straight')
            straight_text = 'Go straight'
            cv2.putText(frame, straight_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)

    else:
        print('go straight')
        straight_text = 'Go straight'
        cv2.putText(frame, straight_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)

    cv2.imshow('path video', frame)
    key = cv2.waitKey(1)
    if key == 27: #press esc to exit
        break

cap.release()
cv2.destroyAllWindows()
