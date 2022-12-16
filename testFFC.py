import cv2
import numpy as np

def flatFieldCorrection(rawImg):
    print("in FFC")
    flatImg = cv2.imread("FlatImg.bmp")
    darkImg = cv2.imread("DarkImg.bmp")

    flatImg = cv2.cvtColor(flatImg, cv2.COLOR_BGR2GRAY)
    darkImg = cv2.cvtColor(darkImg, cv2.COLOR_BGR2GRAY)

    fdImg = np.asarray(flatImg-darkImg)
    m = int(np.average(fdImg))
    print(m)

    arr1 = rawImg - darkImg
    arr2 = flatImg - darkImg

    arg1 = np.multiply(arr1, m)

    correctedImg = np.divide(arg1, arr2)
    cv2.imshow("flat-dark", fdImg)
    cv2.imshow("flat", flatImg)
    cv2.imshow("raw", rawImg)
    return correctedImg

img = cv2.imread("beamImg.bmp")

img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

cv2.imshow("test", flatFieldCorrection(img))
while True:
    if cv2.waitKey(1) & 0xff == ord('q'):
        break
cv2.destroyAllWindows()