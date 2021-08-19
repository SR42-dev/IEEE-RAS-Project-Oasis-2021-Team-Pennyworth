'''
# to print values onto spreadsheet 
x = [[2,5],[56,77]]
response = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,range="Sheet1!B5:C6",valueInputOption="USER_ENTERED",body={"values":x}).execute()
'''

'''
# Rough work
img = cv2.imread(r'resources/CaptureS.JPG')

mask = cv2.inRange(hsv, lower, upper)

frame=cv2.GaussianBlur(img,(5,5),cv2.BORDER_DEFAULT)
image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
path_mask = cv2.inRange(image, path_lower, path_upper)
cv2.imshow("mask", path_mask)
cv2.imshow("webcam", img)
'''

'''
# Video feed
path_lower = np.array([15, 85, 150])
path_upper = np.array([50, 255, 255])
video = cv2.VideoCapture(0)
while True:
    success, img = video.read()
    frame=cv2.GaussianBlur(img,(5,5),cv2.BORDER_DEFAULT)
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    path_mask = cv2.inRange(image, path_lower, path_upper)
    cv2.imshow("mask", path_mask)
    cv2.imshow("webcam", img)

    key = cv2.waitKey(1)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
'''

'''
def getColorCode(img,col1) :
 
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    if col1 == 'black' :
        return np.uint8([[[0, 0, 0]]])
    elif col1 == 'white' :
        return np.uint8([[[255, 255, 255]]])
    elif col1 == 'red' :
        return np.uint8([[[255, 0, 0]]])
    elif col1 == 'green' :
        return np.uint8([[[0, 255, 0]]])
    elif col1 == 'blue' :
        return np.uint8([[[0, 0, 255]]])
    elif col1 == 'yellow' :
        return np.uint8([[[255, 255, 0]]])
    elif col1 == 'cyan' :
        return np.uint8([[[0, 255, 255]]])
    elif col1 == 'magenta' :
        return np.uint8([[[255, 0, 255]]])
    elif col1 == 'gokul':
        lower = np.array([15, 85, 150]) # Finding HSV limits directly and supplying as arguments for cv2.inRange(.)
        upper = np.array([50, 255, 255])

    return lower, upper
'''
