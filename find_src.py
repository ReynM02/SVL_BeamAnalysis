import json
import cv2
import numpy as np
import matplotlib.pyplot as plt
def unwarp(img, src, dst, testing):
    h, w = img.shape[:2]
    # use cv2.getPerspectiveTransform() to get M, the transform matrix, and Minv, the inverse
    M = cv2.getPerspectiveTransform(src, dst)
    # use cv2.warpPerspective() to warp your image to a top-down view
    warped = cv2.warpPerspective(img, M, (w, h), flags=cv2.INTER_LINEAR)

    if testing:
        f, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
        f.subplots_adjust(hspace=.2, wspace=.05)
        ax1.imshow(img)
        x = [src[0][0], src[2][0], src[3][0], src[1][0], src[0][0]]
        y = [src[0][1], src[2][1], src[3][1], src[1][1], src[0][1]]
        ax1.plot(x, y, color='red', alpha=0.4, linewidth=3, solid_capstyle='round', zorder=2)
        ax1.set_ylim([h, 0])
        ax1.set_xlim([0, w])
        ax1.set_title('Original Image', fontsize=30)
        ax2.imshow(cv2.flip(warped, 1))
        ax2.set_title('Unwarped Image', fontsize=30)
        plt.show()
    else:
        return warped

def loadConfig(light_string):
    filePath = "configs/"+light_string+".json"
    try:
        with open(filePath, 'r') as file:
            print("found config")
            data = json.load(file)
    except FileNotFoundError:
        return 1
    return data

data = loadConfig("system_setup")
src = np.float32(data["src"])
print(src)
dst = np.float32(data["dst"])
image = cv2.imread("DEWARP IMAGE 12-15-2022.bmp")
bwImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

ret,thresh = cv2.threshold(bwImage,75,255,0)
otherindex = np.where(thresh < 255)
cv2.line(thresh, (130, 108), (1352, 89) ,(0), 2)
cv2.line(thresh, (130, 108), (300, 908) ,(0), 2)
cv2.line(thresh, (1352, 89), (1190, 905) ,(0), 2)
cv2.imshow("test", thresh)
warpedim = unwarp(image, src, dst, False)
cv2.imshow("unwarp", warpedim)

while True:
    if cv2.waitKey(1) & 0xff == ord('q'):
        break
cv2.destroyAllWindows()
