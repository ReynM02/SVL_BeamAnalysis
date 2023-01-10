from vimba import *
import cv2
import serial
import time
yes = 0
with Vimba.get_instance() as vimba:
    cams = vimba.get_all_cameras()
    arduino = serial.Serial('COM8', 9600)
    time.sleep(1)
    ready = arduino.read_all()
    print(ready)
    print('cams obtained')
    with cams[0] as cam:
        print('cam[0] found')
        while True:
            msg = 'C10'
            #print(msg)
            msgbyte = bytes(msg, 'utf-8')
            print(msgbyte)
            arduino.write(msgbyte)
            #time.sleep(1)
            try:
                frame = cam.get_frame()
                frame.convert_pixel_format(PixelFormat.Bgr8)
            #print('frame grabbed')
                image = frame.as_opencv_image()
            #print('image converted to opencv')
                yes = yes+1
            except:
                print("timeout")
            cv2.imshow('im', image)
            print(yes)
            serIn = arduino.read_all()
            print(serIn)
            if cv2.waitKey(1) & 0xff == ord('q'):
                break
        cv2.destroyAllWindows()