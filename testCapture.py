from cv2 import split
from vimba import *
import cv2
from array import *

with Vimba.get_instance() as vimba:
    cams = vimba.get_all_cameras()
    print('cams obtained')
    with cams[0] as cam:
        print('cam[0] found')
        cam.load_settings("colorSettings.xml", PersistType.All)
        print('color settings loaded')
        frame = cam.get_frame()
        #frame.convert_pixel_format(PixelFormat.Rgb8)
        print('frame grabbed')
        #bgImage = frame.as_opencv_image()
        #ToDo: Trigger Light
        #frame = cam.get_frame()
        #fgImage = frame.as_opencv_image()
        test = False
        image = frame.as_opencv_image()
        print('image converted to opencv')

lightColor = input('R=RED, B=BLU, W=WHI')
b, g, r = cv2.split(image)

if lightColor == "W":
        fgImage = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        #bgImage = cv2.cvtColor(bgImage, cv2.COLOR_RGB2GRAY)
        #image = cv2.absdiff(fgImage, bgImage)
        #image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
elif lightColor == "B":
        bgImage = cv2.split(image)
        #fgImage = cv2.split(fgImage)
        #image = cv2.absdiff(fgImage[1], bgImage[1])
        #image = b
elif lightColor == "R":
        bgImage = cv2.split(image)
        #fgImage = cv2.split(fgImage)
        #image = cv2.absdiff(fgImage[3], bgImage[3])
        #image = r

cv2.imshow('r', r)
cv2.imshow('g', g)
cv2.imshow('b', b)
cv2.imshow('fr', image)
while True:
        if cv2.waitKey(1) & 0xff == ord('q'):
                break
cv2.destroyAllWindows()