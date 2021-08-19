import cv2
import numpy as np
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from pprint import pprint
SERVICE_ACCOUNT_FILE = 'project-oasis-pennyworth-0b253f0db19d.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = None
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes = SCOPES)

SAMPLE_SPREADSHEET_ID = '1K_bkaptNKItZoP3F97W0wpgdHbY-fl-3zNuK2zqnooc'
service = build('sheets','v4',credentials = creds)

sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,range = "Sheet1!A1").execute()
values = result.get('values', [])

barrier_color = values[0][0]

file_location = 'Task_3-InputVideo.mp4'

cap = cv2.VideoCapture(file_location)
cap.set(3,1280)
cap.set(4,720)

font = cv2.FONT_HERSHEY_COMPLEX

path_lower = np.array([115,35,60]) #for blue ink
path_upper = np.array([133,255,255])

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

kernel = np.ones((5,5),np.uint8)
stop_variable = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print('video ended')
        break
    (h, w) = frame.shape[:2]
    blur = cv2.GaussianBlur(frame,(5,5),cv2.BORDER_DEFAULT)
    hsvvid = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    path_mask = cv2.inRange(hsvvid, path_lower, path_upper)
    opening = cv2.morphologyEx(path_mask, cv2.MORPH_OPEN, kernel)
    erosion = cv2.erode(opening,kernel,iterations = 3)
    dilation = cv2.dilate(erosion,kernel,iterations = 5)
    path_contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    barrier_mask = getmask(hsvvid, barrier_color)
    barrier_contours, hierarchy = cv2.findContours(barrier_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(barrier_contours) != 0:
        sorted_barrier_contours = sorted(barrier_contours, key=cv2.contourArea, reverse= False)
        if stop_variable == 0:

            for barrier_contour in sorted_barrier_contours:
                x_barrier, y_barrier, w_barrier, h_barrier = cv2.boundingRect(barrier_contour)

                if w_barrier*h_barrier > 200000:
                    stop_variable = 1
                    print('stop')
                    stop_text = 'Stop'
                    cv2.putText(frame, stop_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)
                    break

                elif len(path_contours) > 1:
                    sorted_path_contours= sorted(path_contours, key=cv2.contourArea, reverse= False)

                    if cv2.contourArea(sorted_path_contours[0]) > 1000 or cv2.contourArea(sorted_path_contours[1]) > 1000:
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

        else:
            print('stop')
            stop_text = 'Stop'
            cv2.putText(frame, stop_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)

    elif len(path_contours) > 1:
        stop_variable = 0
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
        stop_variable = 0
        print('go straight')
        straight_text = 'Go straight'
        cv2.putText(frame, straight_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)

    cv2.imshow('path video', frame)
    key = cv2.waitKey(20)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
