import cv2
import numpy as np
import serial
import time
import mediapipe as mp
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

ser = serial.Serial('/dev/ttyACM0', baudrate = 9600, timeout = 1)

table = input("table: ")
name = input("customer name")

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

def getmask(hsvframe, colorchoice):
    if colorchoice == 'black':
        return cv2.inRange(hsvframe, black_lower, black_upper)
    elif colorchoice == 'violet':
        return cv2.inRange(hsvframe, violet_lower, violet_upper)
    elif colorchoice == 'pink':
        return cv2.inRange(hsvframe, pink_lower, pink_upper)

while True:
    ret, frame = cap.read()
    if not ret:
        cap = cv2.VideoCapture(0)
        continue
    (h, w) = frame.shape[:2]
    blur = cv2.GaussianBlur(frame,(5,5),cv2.BORDER_DEFAULT)
    hsvvid = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    table_mask = getmask(hsvvid, table)
    table_contours, hierarchy = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    opening = cv2.morphologyEx(path_mask, cv2.MORPH_OPEN, kernel)
    erosion = cv2.erode(opening,kernel,iterations = 1)
    dilation = cv2.dilate(erosion,kernel,iterations = 5)
    path_contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(table_contours) > 0:
        largest_table = max(table_contours, key = cv2.contourArea)
        x_table, y_table, w_table, h_table = cv2.boundingRect(largest_table)
        if w_table*h_table > 100:
            break

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

x = [['Customer', name], ['Rating', rating]]
response = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet1!A2:B3", valueInputOption="USER_ENTERED", body={"values": x}).execute()
