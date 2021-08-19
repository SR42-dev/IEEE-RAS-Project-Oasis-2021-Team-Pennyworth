import cv2
import serial
import time
import numpy as np
import mediapipe as mp
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Line following algorithm

path_lower = np.array([0,80,0]) # Yellow : Path, values found using trackbars
path_upper = np.array([178,255,255])

colour1_upper = np.array([0,90,0]) # Black : switch to right track
colour1_lower = np.array([179,255,130])

colour2_upper = np.array([120,120,0]) # Violet : switch to left track
colour2_lower = np.array([140,255,255])

colour3_upper = np.array([120,60,0]) # Pink : move to center of board and keep going till a line is reacquired
colour3_lower = np.array([179,150,255])

count_color = 0

ser = serial.Serial('/dev/ttyACM0', baudrate = 9600, timeout = 1)

cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)

font = cv2.FONT_HERSHEY_COMPLEX
kernel = np.ones((5,5),np.uint8)

while True:
    ret, frame = cap.read()
    if not ret:
        cap = cv2.VideoCapture(0)
        continue
    (h, w) = frame.shape[:2]
    blur = cv2.GaussianBlur(frame,(5,5),cv2.BORDER_DEFAULT)
    hsvvid = cv2.cvtColor(blur, cv2.COLOR_BGR)

    path_mask = cv2.inRange(hsvvid, path_lower, path_upper)
    colour1_mask = cv2.inRange(hsvvid, colour1_lower, colour1_upper)
    colour2_mask = cv2.inRange(hsvvid, colour2_lower, colour2_upper)
    colour3_mask = cv2.inRange(hsvvid, colour3_lower, colour3_upper)
    colour1_contours, hierarchy = cv2.findContours(colour1_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    colour2_contours, hierarchy = cv2.findContours(colour2_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    colour3_contours, hierarchy = cv2.findContours(colour3_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    opening = cv2.morphologyEx(path_mask, cv2.MORPH_OPEN, kernel)
    erosion = cv2.erode(opening,kernel,iterations = 1)
    dilation = cv2.dilate(erosion,kernel,iterations = 5)
    path_contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Condition check for colour coded instructions

    if len(colour1_contours) > 0 and cv2.contourArea(colour1_contour[0]) > 100:
        count_color += 1
        cv2.putText(frame, 'Switching tracks ...', (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)
        for a in range(12): # change range parameter according to test
            i = 'r'
            ser.write(i.encode())
            time.sleep(0.050)


    elif len(colour2_contours) > 0 and cv2.contourArea(colour2_contour[0]) > 100:
        count_color += 1
        cv2.putText(frame, 'Switching tracks ...', (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)
        for a in range(12): # change range parameter according to test
            i = 'l'
            ser.write(i.encode())
            time.sleep(0.050)

    elif len(colour3_contours) > 0 and cv2.contourArea(colour3_contour[0]) > 100:
        count_color += 1
        cv2.putText(frame, 'Moving to center', (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)
        for a in range(20): # change range parameter according to test
            i = 'r'
            ser.write(i.encode())
            time.sleep(0.050)
        for a in range(5):
            i = 'f'
            ser.write(i.encode())
            time.sleep(0.175)
        ser.write(i.encode())
        while len(path_contours) == 0:
            i = 'f'
            ser.write(i.encode())
            time.sleep(0.175)


    elif len(path_contours) > 0:
        largest = max(path_contours, key = cv2.contourArea)
        cnt_1 = largest
        M_1 = cv2.moments(cnt_1)
        path_centroid_x = int(M_1['m10']/M_1['m00'])
        path_centroid_y = int(M_1['m01'] / M_1['m00'])

        if path_centroid_x < w/2 - 150:
            i = 'l'
            ser.write(i.encode())
            print('go left')
            left_text = 'Go left'
            cv2.putText(frame, left_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(0.050)
        elif path_centroid_x > w/2 + 150:
            i = 'r'
            ser.write(i.encode())
            print('go right')
            right_text = 'Go right'
            cv2.putText(frame, right_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(0.050)
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
        print('right')
        straight_text = 'right'
        cv2.putText(frame, straight_text, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)
        time.sleep(0.175)

    cv2.imshow('path video', frame)

    if (cv2.waitKey(1) & 0xFF == ord('q')) or (count_color > 3):
        break

cap.release()
cv2.destroyAllWindows()

# Gesture based rating system

# Google sheets link : https://docs.google.com/spreadsheets/d/1kLxCUNyn39Q1-B3KkvbxDz2Vc4NFZVxhb0AwKGzeZbI/edit#gid=0
SERVICE_ACCOUNT_FILE = 'key.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SAMPLE_SPREADSHEET_ID = '1kLxCUNyn39Q1-B3KkvbxDz2Vc4NFZVxhb0AwKGzeZbI'

creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()


class handDetector():

    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):

        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:

            for handLms in self.results.multi_hand_landmarks:

                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)

        return img

    def findPosition(self, img, handNo=0, draw=True):

        lmList = []

        if self.results.multi_hand_landmarks:

            myHand = self.results.multi_hand_landmarks[handNo]

            for id, lm in enumerate(myHand.landmark):

                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])

                if draw:
                    cv2.circle(img, (cx, cy), 15, (33, 32, 196), cv2.FILLED)

        return lmList


wCam, hCam = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
detector = handDetector(detectionCon=0.75)
tipIds = [4, 8, 12, 16, 20]
rating = 0
rating1 = 0
rating2 = 0
i = 0

while True:

    rating2 = rating1
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:

        fingers = []

        if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:

            fingers.append(1)

        else:

            fingers.append(0)

        for id in range(1, 5):

            if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:

                fingers.append(1)

            else:

                fingers.append(0)

        totalFingers = fingers.count(1)

        # print(totalFingers)

        if totalFingers == 0:
            h = '0'
            rating1 = 0
            cv2.putText(img, h, (100, 250), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

        if totalFingers == 1:
            h = '1'
            rating1 = 1
            cv2.putText(img, h, (100, 250), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

        if totalFingers == 2:
            h = '2'
            rating1 = 2
            cv2.putText(img, h, (100, 250), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

        if totalFingers == 3:
            h = '3'
            rating1 = 3
            cv2.putText(img, h, (100, 250), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

        if totalFingers == 4:
            h = '4'
            rating1 = 4
            cv2.putText(img, h, (100, 250), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

        if totalFingers == 5:
            h = '5'
            rating1 = 5
            cv2.putText(img, h, (100, 250), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    cv2.rectangle(img, (50, 200), (175, 270), (0, 255, 0), 2)
    cv2.putText(img, 'Rating (Backhand)', (50, 185), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 3)
    cv2.imshow("Rating", img)

    if rating1 == rating2:

        i += 1

        if i > 20:
            rating = rating1
            time.sleep(2)
            cv2.destroyAllWindows()
            cap.release()
            break

    elif rating1 != rating2:

        i = 0

    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        cap.release()
        break

# print(rating)

'''
    Notes :

        - Could update n for each successive customer
        - Can format string in sheet.values().update(range) to change input cell for each successive customer

'''

n = 1
x = [['Customer', n], ['Rating', rating]]
response = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet1!A2:B3", valueInputOption="USER_ENTERED", body={"values": x}).execute()


