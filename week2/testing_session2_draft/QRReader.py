from pyzbar.pyzbar import decode
from serial import Serial
import time
import cv2




def write_read(x):
    x = str(x)[2]
    arduino.write(bytes(x, 'utf-8'))
    time.sleep(0.05)
    data = arduino.readline()
    return data


def BarcodeReader(image):
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





while True:

    Hello = cv2.VideoCapture(0)
    hi, bye = Hello.read()
    BarcodeReader(bye)
    k = cv2.waitKey(100)

    if k == 97:
        Hello.release()
        cv2.destroyAllWindows()
        break