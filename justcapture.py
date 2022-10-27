from vimba import *
import cv2

with Vimba.get_instance() as vimba:
    cams = vimba.get_all_cameras()
    print('cams obtained')
    with cams[0] as cam:
        print('cam[0] found')
        while True:
            frame = cam.get_frame()
            frame.convert_pixel_format(PixelFormat.Bgr8)
            #print('frame grabbed')
            image = frame.as_opencv_image()
            #print('image converted to opencv')
            cv2.imshow('im', image)
            if cv2.waitKey(1) & 0xff == ord('q'):
                break
        cv2.destroyAllWindows()