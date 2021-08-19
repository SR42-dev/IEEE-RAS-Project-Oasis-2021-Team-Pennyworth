import cv2
import numpy as np
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account

# Google sheets link : https://docs.google.com/spreadsheets/d/1kLxCUNyn39Q1-B3KkvbxDz2Vc4NFZVxhb0AwKGzeZbI/edit#gid=0

# Retrieves colour from spreadsheet (edit SAMPLE_SPREADSHEET_ID based on spreadsheet URL)
def getSpreadsheetColour(SERVICE_ACCOUNT_FILE = 'key.json', SCOPES = ['https://www.googleapis.com/auth/spreadsheets'], SAMPLE_SPREADSHEET_ID = '1kLxCUNyn39Q1-B3KkvbxDz2Vc4NFZVxhb0AwKGzeZbI') :

    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="sheet1!A1:J10").execute()
    values = result.get('values', [])
    return values[0][0] # Colour retrieved from cell A1

# Processes colour from string to numpy.ndarray format containing RGB limits (to be fed to cv2.inRange)
def getColorCode(col1) :

    if col1 == 'red' :
        lower = np.uint8([[[0,115,145]]])
        upper = np.uint8([[[9,255,255]]])
    elif col1 == 'green' :
        lower = np.uint8([[[35,75,115]]])
        upper = np.uint8([[[55,255,255]]])
    elif col1 == 'blue' :
        lower = np.uint8([[[101, 100, 20]]])
        upper = np.uint8([[[130, 255, 255]]])
    elif col1 == 'magenta':
        lower = np.uint8([[[146, 100, 20]]])
        upper = np.uint8([[[152, 255, 255]]])
    #elif col1 == 'yellow' : # Commented as yellow is the track color
        #lower = np.uint8([[[22, 93, 0]]])
        #upper = np.uint8([[[45, 255, 255]]])

    return lower, upper

# Generates upper & lower limits for colour detection (abandoned)
def generateColorLimits(frame, col1):

    '''
    # Adapted from this... thing.. that I lifted off of stackoverflow verbatim
    # Converts RBG value triplet to upper and lower colour limits in HSV format
    import numpy as np
    import cv2

    green = np.uint8([[[255, 0, 255]]]) #here insert the bgr values which you want to convert to hsv
    hsvGreen = cv2.cvtColor(green, cv2.COLOR_BGR2HSV)
    print(hsvGreen)

    lowerLimit = hsvGreen[0][0][0] - 10, 100, 100
    upperLimit = hsvGreen[0][0][0] + 10, 255, 255

    print(lowerLimit)
    print(upperLimit)
    '''

    hsvCol1 = cv2.cvtColor(col1, cv2.COLOR_BGR2HSV)

    lowerLimit = hsvCol1[0][0][0] - 10, 100, 100
    upperLimit = hsvCol1[0][0][0] + 10, 255, 255

    lowerLimit = np.array(lowerLimit)
    upperLimit = np.array(upperLimit)

    return frame, lowerLimit, upperLimit # to be fed to cv2.inRange(.) for masking or to checkStop()

# Checks if retrieved color is detected on image
def checkStop(frame, lower, upper) : # Revisit return conditions

    #image = cv2.resize(img, (700, 600))
    #hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    #mask = cv2.inRange(hsv, lower, upper)


    (h, w) = frame.shape[:2]
    blur = cv2.GaussianBlur(frame, (5, 5), cv2.BORDER_DEFAULT)
    hsvvid = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    color_mask = cv2.inRange(hsvvid, lower, upper)
    color_contours, hierarchy = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(color_contours) != 0:
        sorted_color_contours = sorted(color_contours, key=cv2.contourArea, reverse=False)
        for color_contour in sorted_color_contours:
            x_color, y_color, w_color, h_color = cv2.boundingRect(color_contour)
            if w_color * h_color > 200000 : # change conditions based on threshold area
                return True;
            else :
                return False;

    #cv2.imshow('mask', mask)

    '''
    # Checking for significant coloured area
    mask_contour, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if cv2.contourArea(mask_contour) > 500:
        return True
    '''
    #return [[255,255,255]] in mask # Returns true if colour within range is detected


