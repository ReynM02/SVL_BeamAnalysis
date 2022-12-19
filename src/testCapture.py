from cv2 import split
from vimba import *
import cv2
from array import *

def capture(): #Captures Image, Performs Background Subtraction, Determines Test Mode
    try:
        with Vimba.get_instance() as vimba:
            cams = vimba.get_all_cameras()
            print('cams obtained')
            #print(exp)
            with cams[0] as cam:
                print('cams[0] found')
                #cam.load_settings("colorSettings.xml", PersistType.All)
                print('color settings loaded')
                print('cam got')
                #exposure_time.set(500)
                #print('expt set')
                frame = cam.get_frame()
                print('frame grabbed')
                #bgImage = frame.as_opencv_image()
                #ToDo: Trigger Light
                #frame = cam.get_frame()
                #fgImage = frame.as_opencv_image()
                test = False
                frame.convert_pixel_format(PixelFormat.Bgr8)
                image = frame.as_opencv_image()
                print('image converted to opencv')
    except:
        print('in except')
        image = cv2.imread("test_1.PNG")
        print('image loaded')
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        print('image converted to mono')
        test = True
        
    
    #if test == False:
    #    if lightColor == "WHI":
     #       fgImage = cv2.cvtColor(fgImage, cv2.COLOR_RGB2GRAY)
      #      bgImage = cv2.cvtColor(bgImage, cv2.COLOR_RGB2GRAY)
       #     image = cv2.absdiff(fgImage, bgImage)
        #elif lightColor == "470":
        #    bgImage = cv2.split(bgImage)
         #   fgImage = cv2.split(fgImage)
          #  image = cv2.absdiff(fgImage[1], bgImage[1])
        #elif lightColor == "625":
         #   bgImage = cv2.split(bgImage)
          #  fgImage = cv2.split(fgImage)
           # image = cv2.absdiff(fgImage[3], bgImage[3])

        #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    print('returned image')
    return image, test

image, test = capture()
print('image got')

print(test)
cv2.imshow('t', image)
while True:
        if cv2.waitKey(1) & 0xff == ord('q'):
                break
cv2.destroyAllWindows()