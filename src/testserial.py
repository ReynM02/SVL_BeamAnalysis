import serial
import time
ser = serial.Serial("COM8", 9600)
time.sleep(1)
input = ser.read_all()
print(input)
msg = bytes('C100', 'utf-8')
print(msg)
ser.write(msg)
time.sleep(3)
input = ser.read_all()
print(input)

def trythis(exp):
    print("in CaptureExt()")
    #try:
    msg = 'C' + str(exp)
    print(msg)
    msgbyte = bytes(msg, 'utf-8')
    print(msgbyte)
    ser.write(msgbyte)
    print("written to arduino")

trythis(100)