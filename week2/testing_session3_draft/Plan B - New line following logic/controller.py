import serial
import time

ser = serial.Serial('/dev/ttyACM0', baudrate = 9600, timeout = 1)

while True:
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
    else:
        break
