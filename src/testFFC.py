import cv2
import numpy as np

def flatFieldCorrection(rawImg):
    print("in FFC")
    flatImg = cv2.imread("FlatImg.bmp")
    darkImg = cv2.imread("DarkImg.bmp")

    flatImg = cv2.cvtColor(flatImg, cv2.COLOR_BGR2GRAY)
    darkImg = cv2.cvtColor(darkImg, cv2.COLOR_BGR2GRAY)



    arr1 = rawImg - darkImg
    arr2 = flatImg - darkImg

    otherIndex = np.where(flatImg > 0)

    total = 0
    count = 0
    rowcount = 0
    flux = 0

    row_start = otherIndex[0][0]
    row_end = otherIndex[0][-1]
    minVal = np.asarray(otherIndex[1]).min()
    maxVal_2 = np.asarray(otherIndex[1]).max()
    

    row = otherIndex[0][0]
    row_max = otherIndex[0][-1]
        
    while row <= row_max:
        col = minVal
        col_max = maxVal_2
        while col <= col_max:
            flux = flux + flatImg[row-1][col-1]
            col = col+1
            count = count + 1
        row = row+1

    average = flux / count

    print(average)

    m = np.average(arr2)
    print(m)

    arg1 = arr1 * m

    correctedImg = arg1 / arr2
    
    correctedImg = ( ( rawImg - darkImg ) * m ) / (flatImg - darkImg)

    cv2.imshow("flat-dark", arr2)
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