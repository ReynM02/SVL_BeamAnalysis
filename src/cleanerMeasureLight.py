from vimba import *
import cv2
import numpy as np
import datetime
from array import *
import lut
import json
import serial
import time
import find_ports as fp

# Final image scale factors
manta = 0.95   # 1
alvium = 0.75 # 2

arduino = serial.Serial()
arduino.baudrate = 19200

documentPath = ""

class NotAListError(Exception): ...

class LoadBarLevel:
    level = 0

    def __init__(self, window = None, max = None):
        self.window = window
        self.max = max

    def increase(self, last = False):
        if self.max == None:
            self.level += 1
        elif self.max != None and self.level < self.max:
            if last == False:
                self.level += 1
            else:
                diff = self.max - self.level
                self.level += diff
        else:
            self.level = self.level
        print(self.level)
        if self.window != None:
            self.window.write_event_value('update_-PROG-', self.level)

class MeasuredData:
    flux = int
    lux = int
    symmetry = [int, int]
    boxMiddle = [int, int]
    size = [int, int]
    contPeak = str
    odPeak = str
    npnCurrent = str
    pnpHiCurrent = str
    pnpLoCurrent = str
    analogHi = str
    analogLo = str
    beamImg = []
    intensityImg = []
    beamPf = []
    intensityPf = []
    currentPf = []
    graphs = []
    symGood = []

    def __init__(self):
        self.flux = None
        self.lux = None
        self.symmetry = [None, None]
        self.size = [None, None]
        self.contPeak = None
        self.odPeak = None
        self.npnCurrent = None
        self.pnpHiCurrent = None
        self.pnpLoCurrent = None
        self.analogHi = None
        self.analogLo = None
        self.beamImg = None
        self.intensityImg = None
        self.beamPf = [None, None]
        self.intensityPf = [None, None]
        self.currentPf = [None, None, None, None, None]
        self.graphs = [None, None]
        self.symGood = [None, None]
    
class unused:
    def getList(self, dst):
        attr = getattr(self, dst)
        return attr

    def addList(self, dst):
        setattr(self, dst, [])
    
    def delList(self, dst):
        delattr(self, dst)
        
    def add(self, dst = "", data = list):
        if hasattr(self, dst):
            attr = getattr(self, dst)
            print(vars(self))
            if attr != None:
                print(data)
                attr.extend(data)
            else:
                raise NotAListError
        else:
            self.addList(dst)
            self.add(dst, data)

    def get(self):
        lists = vars(self)
        for i in lists:
            print(i)
            src = self.getList(i)
            self.dataList.extend(src)
        return self.dataList

def connect(progBar = None):
    """
    Finds and connects to arduino. Searches through all availible serial COM ports looking for
    serial message "SLA".

    :param progBar:    Instance of the LoadBarLevel Class
    :type progBar:     LoadBarLevel
    :return:           True if the arduino is found. False if the arduino is not found.
    :rtype:            bool
    """

    if progBar == None:
        progBar = LoadBarLevel()

    readyString = ""
    progBar.increase()
    ports, pnum = fp.run()
    progBar.increase()
    x=0
    #print(ports, pnum)
    while x < pnum:
        print(x)
        progBar.increase()
        arduino.port = ports[x]
        #print(ports[x])
        arduino.open()
        progBar.increase()
        time.sleep(2)
        if arduino.is_open:
            ready = arduino.read_all()
            progBar.increase()
            try:
                readyString = ready.decode("UTF-8")
            except:
                readyString = "not matching baudrate"
            #print(readyString)
            progBar.increase()
        if readyString == 'SLA':
            #print("found it")
            progBar.increase()
            return True
        else:
            arduino.close()
            x += 1
            progBar.increase()
    progBar.increase()
    return False

def unwarpImg(img, src, dst):
    """
    Un-warps an input image based on source co-ordinates and destination co-ordinates.

    :param img:        The image that will be un-warped
    :type img:         ndarray
    :param src:        Source co-ordinates, the points on the warped image
    :type src:         Int array
    :param dst:        Destination co-ordinates, the points where the image will go
    :type dst:         Int array
    :return:           The un-warped image
    :rtype:            ndarray
    """
    print("in unwarp")
    h, w = img.shape[:2]
    print("got H, W")
    # use cv2.getPerspectiveTransform() to get M, the transform matrix, and Minv, the inverse
    M = cv2.getPerspectiveTransform(src, dst)
    print("got perspective")
    # use cv2.warpPerspective() to warp your image to a top-down view
    warped = cv2.warpPerspective(img, M, (w, h), flags=cv2.INTER_LINEAR)
    print("warped img")
    return warped

def flatFieldCorrection(rawImg):
    """
    Performs flat field correction on input image. Takes in an OpenCV image,
    and uses stored dark field and bright field images.

    :param rawImg:        The image that will be un-warped
    :type rawImg:         ndarray
    :return:              The corrected image
    :rtype:               ndarray
    """
    print("in FFC")
    flatImg = cv2.imread("FlatImg.bmp")
    darkImg = cv2.imread("DarkImg.bmp")

    flatImg = cv2.cvtColor(flatImg, cv2.COLOR_BGR2GRAY)
    darkImg = cv2.cvtColor(darkImg, cv2.COLOR_BGR2GRAY)

    fdImg = flatImg-darkImg
    m = np.average(fdImg)
    
    correctedImg = np.asarray(( ( rawImg - darkImg ) * m ) / (flatImg - darkImg), dtype=np.uint8)

    return correctedImg

def Capture(mode, exp, config, loadBar = LoadBarLevel):
    """
    Sets exposure time and saves captured images. Sends message to arduino containing 
    the light mode and exposure time. Waits for arduino to capture image, and then saves 
    and moves on to next image. Captures 2 images, background and forground.

    :param mode:        The image that will be un-warped
    :type mode:         ndarray
    :param exp:        Source co-ordinates, the points on the warped image
    :type exp:         Int array
    :param config:        Destination co-ordinates, the points where the image will go
    :type config:         Int array
    :return:           The intesnity image and the beam image.
    :rtype:            ndarray
    """

    with Vimba.get_instance() as vimba:
        loadBar.increase()
        cams = vimba.get_all_cameras()
        cams[0].set_access_mode(AccessMode.Full)
        loadBar.increase()
        with cams[0] as cam:
            loadBar.increase()
            print("in CaptureExt()")
            print('cam[0] found')
            loadBar.increase()
            try:
                expTime = cam.ExposureTime
            except Exception as e:
                print(e)
            loadBar.increase()
            print('exp calc')
            try:
                expTime.set(exp)
            except Exception as e:
                print(e)
            print("exp set")
            loadBar.increase()
            msg = str(mode) + str(exp/1000)
            print("msg created")
            loadBar.increase()
            msgbyte = bytes(msg, 'utf-8')
            print(msgbyte)
            print("msg converted to byte")
            loadBar.increase()
            try:
                arduino.write(msgbyte)
            except:
                raise Exception("NoCntrlr")
            print("msg sent to arduino")
            loadBar.increase()
            hs = None
            print("read duino")
            loadBar.increase()
            try:
                while hs != b'S':
                    print("in loop")
                    hs = arduino.read(1)
                loadBar.increase()
                try:
                    bgframe = cam.get_frame(timeout_ms=5000)
                    loadBar.increase()
                    print("got bgframe")
                    bgframe.convert_pixel_format(PixelFormat.Bgr8)
                    loadBar.increase()
                    print("converted frame")
                    bgimage = bgframe.as_opencv_image()
                    loadBar.increase()
                    print("saved as bgimage")
                    arduino.write(bytes("K", 'utf-8'))
                    loadBar.increase()
                except Exception as e:
                    loadBar.increase()
                    print(e)
                    arduino.write(bytes("K", 'utf-8'))
                    raise Exception("NoPic")
        
                hs = None
                while hs != b'S':
                    hs = arduino.read(1)
                loadBar.increase()
                try:
                    frame = cam.get_frame(timeout_ms=5000)
                    loadBar.increase()
                    print("got frame")
                    frame.convert_pixel_format(PixelFormat.Bgr8)
                    loadBar.increase()
                    print("converted frame")
                    image = frame.as_opencv_image()
                    loadBar.increase()
                    print("image saved as image")
                    arduino.write(bytes("K", 'utf-8'))
                except Exception as e:
                    #print(e)
                    arduino.write(bytes("K", 'utf-8'))
                    loadBar.increase()
                test = False
            except Exception as e:
                loadBar.increase()
                print(e)
                hs = None
                while hs != b'S':
                    hs = arduino.read(1)
                arduino.write(bytes("K", 'utf-8'))
                #arduino.write(bytes("K", 'utf-8'))  
                raise e
            loadBar.increase()
            try:
                image = image - bgimage
            except UnboundLocalError:
                raise UnboundLocalError
            except Exception as e:
                raise e
            loadBar.increase()
    #image = flatFieldCorrection(image)
    print("bg sub done")
    loadBar.increase()
    src = np.float32(config["src"])
    dst = np.float32(config["dst"])
    loadBar.increase()
    unwarped = unwarpImg(image, src, dst)
    print("unwarped image")
    beamImg = unwarped #cv2.GaussianBlur(unwarped, (15,15), 0)
    maxVal = int(beamImg.max())
    loadBar.increase()
    beamImg = np.float32(beamImg/int(maxVal))
    beamImg = beamImg * 255
    loadBar.increase()
    beamImg = beamImg.astype(np.uint8)
    loadBar.increase()
    
    return unwarped, beamImg
#End CaptureExt() 

def loadConfig(light_string):
    filePath = documentPath + "/configs/" + light_string + ".json"
    print(filePath)
    try:
        with open(filePath, 'r') as file:
            print("found config")
            data = json.load(file)
    except FileNotFoundError:
        print("No File")
        return 1
    return data
#End loadConfig()

def beamMeasure(beamImg, configs, loadBar = LoadBarLevel, measuredData = MeasuredData):
    print("in beamMeasure()")
    loadBar.increase()
    # Parse Args    
    lightConfig = configs[0]
    sysConfig = configs[1]
    loadBar.increase()
    # Init Pass/Fail Vars
    pf = [False, False]
    # Grab Lut Exported From Zemax 
    zemaxLut = lut.finalLut
    loadBar.increase()
    # Set Uniformity Value 
    uniformityValue = 255*0.8  #80%

    ## -- Set Pass/Fail Thresholds From Config -- ##
    # - Symmetry
    symmetryGap = lightConfig['symmetry_tolerance']
    # - X Vlaue
    loadBar.increase()
    xHigh = lightConfig['x_good'] + lightConfig["x_tolerance"]
    xLow = lightConfig['x_good'] - lightConfig["x_tolerance"]
    # - Y Value
    loadBar.increase()
    yHigh = lightConfig['y_good'] + lightConfig["y_tolerance"]
    yLow = lightConfig['y_good'] - lightConfig["y_tolerance"]

    bwBeamImg = cv2.cvtColor(beamImg, cv2.COLOR_BGR2GRAY)
    loadBar.increase()
    # Create a Bianary Array, Where Pixels Within The 80% Uniformity Are 1, And Those Outside Are 0.
    # Essentially This is Blob Detection
    try:
        ret,thresh = cv2.threshold(bwBeamImg,uniformityValue,255,0)
        print("thresh img good")
        # Calculate The Moments of The Bianary Image
        M = cv2.moments(thresh)
        print("moments found")
        # Calculate X,Y Co-ordinates of Blob Centroid
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
    except Exception as e:
        # No Moments Found, Set cX and cY to None
        cX = None
        cY = None
        print('no moments found')
        raise e
    if cY != None:
        loadBar.increase()
        # Create an Array of Pixel Locations (x,y) For Pixels With an Intensity
        # Greater Than or Equal to uniformityValue  
        uniformityIndex = np.where(beamImg >= uniformityValue)
        print("uniformity index created")
        loadBar.increase()
        minVal = np.asarray(uniformityIndex[1]).min()
        maxVal = np.asarray(uniformityIndex[1]).max()
        loadBar.increase()
        midpoint_vertical = int((maxVal + minVal) / 2)
        midpoint_horizontal = int((uniformityIndex[0][-1] + uniformityIndex[0][0]) / 2)
        loadBar.increase()
        # Define x and y start/end values for cross section profiles
        y_start = uniformityIndex[0][0]
        y_end = uniformityIndex[0][-1]
        x_start = minVal
        x_end = maxVal
        loadBar.increase()
        # Define length of horizontal and vertical cross section array
        horiz_length = int((maxVal-minVal) / sysConfig["ppm_calibration"])
        vert_length = int((uniformityIndex[0][-1]-uniformityIndex[0][0]) / sysConfig["ppm_calibration"]) 
        horizontal_profile = np.arange(maxVal-minVal)
        vertical_profile = np.arange(uniformityIndex[0][-1]-uniformityIndex[0][0])
        loadBar.increase()
        # Arrange the plot cross section data
        horiz_x = np.array(range(maxVal-minVal))
        horiz_y = horizontal_profile
        vert_x = np.array(range(uniformityIndex[0][-1]-uniformityIndex[0][0]))
        vert_y = vertical_profile
        loadBar.increase()
        horiz = [horiz_x, horiz_y]
        vert = [vert_x, vert_y]
        loadBar.increase()
        graphs = [horiz, vert]
        # graphs[0] = horiz, graphs[1] = vert
        loadBar.increase()
        # Convert mono to RGB
        rgbBeamImg = cv2.cvtColor(bwBeamImg, cv2.COLOR_GRAY2RGB)
        # Apply Custom LUT
        rgbBeamImg = cv2.LUT(rgbBeamImg, zemaxLut)
        loadBar.increase()
        #Draw 80% Box
        cv2.rectangle(rgbBeamImg, (minVal, uniformityIndex[0][0]), (maxVal, uniformityIndex[0][-1]),
            (255, 255, 255), 2)
        loadBar.increase()
        # Draw Cross Section Lines For Visual Feedback
        cv2.line(rgbBeamImg, (cX, uniformityIndex[0][0]), (cX, uniformityIndex[0][-1]) ,(0, 0, 0), 2)
        cv2.line(rgbBeamImg, (minVal, cY), (maxVal, cY), (0, 0, 0), 2)
        loadBar.increase()
        #Draw Center of 80% Rectangle and Label
        cv2.circle(rgbBeamImg, (midpoint_vertical, midpoint_horizontal), 5, (0,0,0), -1)
        cv2.putText(rgbBeamImg, "box center", (midpoint_vertical - 25, midpoint_horizontal - 25),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)
        loadBar.increase()
        # Draw Centroid of Beam and Label
        cv2.circle(rgbBeamImg, (cX, cY), 5, (0,0,0), -1)
        cv2.putText(rgbBeamImg, "centroid", (cX - 25, cY - 25),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)
        loadBar.increase()
        ## PASS/FAIL CALCULATION ##
        # -- Symmetry
        if midpoint_vertical-cY < symmetryGap and cX-midpoint_horizontal < symmetryGap:
            # Symmetry Passed
            pf[0] = True
        symGood = [cX-midpoint_horizontal, midpoint_vertical-cY]
        loadBar.increase()
        # -- X,Y Value
        if horiz_length > xLow and horiz_length < xHigh and vert_length > yLow and vert_length < yHigh:
            # X Passed
            pf[1] = True 
        loadBar.increase()
        results = [pf, symGood, cY, cX, horiz_length, vert_length]
        #             0     1      2     3   4         5          6
    
    global alvium
    try:
        p = alvium
        w = int(rgbBeamImg.shape[1] * p)
        h = int(rgbBeamImg.shape[0] * p)
    except:
        p = w = h = 0
        p = w = h = 0

    res_img = cv2.resize(rgbBeamImg, (w,h))
    
    measuredData.beamImg = res_img
    measuredData.beamPf = pf
    measuredData.symmetry = [cX, cY]
    measuredData.symGood = symGood
    measuredData.size = [horiz_length, vert_length]
    measuredData.boxMiddle = [midpoint_horizontal, midpoint_vertical]
    
    return rgbBeamImg, results

def intensityMeasure(images, configs, loadBar = LoadBarLevel, measuredData = MeasuredData):
    ## Parse Args ##
    intensityImg = images[0]
    beamImage = images[1]
    loadBar.increase()
    lightConfig = configs[0]
    sysConfig = configs[1]
    loadBar.increase()
    # Set Uniformity Value 
    uniformityValue = 255*0.8  #80%
    loadBar.increase()
    ## -- Set Pass/Fail Thresholds From Config -- ##
    # - Intensity
    intensityHigh = lightConfig['flux_good'] + lightConfig["flux_tolerance"]
    intensityLow = lightConfig['flux_good'] - lightConfig["flux_tolerance"]
    loadBar.increase()
    # Initiate Flux Value
    flux = 0
    lux = 0
    loadBar.increase()
    # Blur The Image
    print('test false')
    bwBeamImg = cv2.cvtColor(beamImage, cv2.COLOR_BGR2GRAY)
    lightColor = lightConfig["color"]
    if lightColor == "WHI":
        bwImage = cv2.cvtColor(intensityImg, cv2.COLOR_BGR2GRAY)
    else:
        b, g, r = cv2.split(intensityImg)
        if lightColor == "470":
            bwImage = b
        elif lightColor == "530":
            bwImage = g
        elif lightColor == "625":
            bwImage = r
        else:
            bwImage = cv2.cvtColor(intensityImg, cv2.COLOR_BGR2GRAY)
    print ('converted bwImage')
    loadBar.increase()
    try:
        ret,thresh = cv2.threshold(bwBeamImg,uniformityValue,255,0)
        print("thresh img good")
        # Calculate The Moments of The Bianary Image
        M = cv2.moments(thresh)
        print("moments found")
        # Calculate X,Y Co-ordinates of Blob Centroid
        
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
    except Exception as e:
        # No Moments Found, Set cX and cY to None
        cX = None
        cY = None
        print('no moments found')
        raise e
    if cY != None:
        loadBar.increase()
        # Create an Array of Pixel Locations (x,y) For Pixels With an Intensity
        # Greater Than or Equal to uniformityValue  
        uniformityIndex = np.where(bwBeamImg >= uniformityValue)
        loadBar.increase()
        minVal = np.asarray(uniformityIndex[1]).min()
        maxVal = np.asarray(uniformityIndex[1]).max()
        loadBar.increase()
        midpoint_vertical = int((maxVal + minVal) / 2)
        midpoint_horizontal = int((uniformityIndex[0][-1] + uniformityIndex[0][0]) / 2)
        loadBar.increase()
        # Define x and y start/end values for cross section profiles
        y_start = uniformityIndex[0][0]
        y_end = uniformityIndex[0][-1]
        x_start = minVal
        x_end = maxVal
        loadBar.increase()
        # Define length of horizontal and vertical cross section array 
        horizontal_profile = np.arange(maxVal-minVal)
        vertical_profile = np.arange(uniformityIndex[0][-1]-uniformityIndex[0][0])
        loadBar.increase()
        # Copy data from image into Horizontal Profile
        x = 0
        if x_end != 0:
            while x_end > x_start:
                x=x+1
                horizontal_profile[x-1] = bwImage[cY][x_end-1]
                x_end = x_end - 1
        print("horizontal profile captured")
        loadBar.increase()
        # Copy data from image into Vertical Profile
        x = 0
        if y_end != 0:
            while y_end > y_start:
                x=x+1
                vertical_profile[x-1] = bwImage[y_end-1][cX]
                y_end = y_end - 1
        print("vertical profile captured")
        loadBar.increase()
        # Arrange the plot cross section data
        horiz_x = np.array(range(maxVal-minVal))
        horiz_y = horizontal_profile
        vert_x = np.array(range(uniformityIndex[0][-1]-uniformityIndex[0][0]))
        vert_y = vertical_profile
        loadBar.increase()

        horiz = [horiz_x, horiz_y]
        vert = [vert_x, vert_y]
        loadBar.increase()

        graphs = [horiz, vert]
        # graphs[0] = horiz, graphs[1] = vert
        loadBar.increase()

        luxHorizontal = np.arange(midpoint_horizontal-int(sysConfig["center_lux_size"]), midpoint_horizontal+int(sysConfig["center_lux_size"]))
        luxvertical = [midpoint_vertical-int(sysConfig["center_lux_size"]), midpoint_vertical+int(sysConfig["center_lux_size"])]
        luxBox = luxHorizontal
        while luxvertical[0]+1 < luxvertical[1]:
            luxBox = np.vstack((luxBox, luxHorizontal))
            luxvertical[0] = luxvertical[0]+1
        loadBar.increase()

        luxMinVal = np.asarray(luxBox[1]).min()
        luxMaxVal = np.asarray(luxBox[1]).max()
        loadBar.increase()

        luxHigh = lightConfig["lux_good"] + lightConfig["lux_tolerance"]
        luxLow = lightConfig["lux_good"] - lightConfig["lux_tolerance"]
        loadBar.increase()

        # Calculate total Flux of 80% rectangle
        row = uniformityIndex[0][0]
        row_max = uniformityIndex[0][-1]
        luxRow = luxBox[0][0]
        luxRow_Max = luxBox[0][-1]
        loadBar.increase()
        while row <= row_max:
            col = minVal
            col_max = maxVal
            while col <= col_max:
                flux = flux + bwImage[row-1][col-1]
                col = col+1
            row = row+1
        loadBar.increase()

        while luxRow <= luxRow_Max:
            col = luxMinVal
            col_max = luxMaxVal
            while col <= col_max:
                lux = lux + bwImage[row-1][col-1]
                col = col+1
            luxRow = luxRow+1
        loadBar.increase()

        nonbiasLux = int(lux / int(lightConfig["exposure"]))

        finalLux = nonbiasLux * int(sysConfig["lux_calibration"])
        pf = [False, False]
        loadBar.increase()
        # -- Flux
        if flux > intensityLow and flux < intensityHigh:
            # Flux Passed
            pf[0] = True
        loadBar.increase()
        # -- LUX
        if finalLux > luxLow and finalLux < luxHigh:
            pf[1] = True
        loadBar.increase()
        results = [flux, finalLux, pf]

    measuredData.flux = flux
    measuredData.lux = finalLux
    measuredData.intensityPf = pf
    measuredData.graphs = graphs

    return results

def currentMeasure(lightConfig, loadBar = LoadBarLevel, measuredData = MeasuredData):
    pf = [False, False, False, False, False]
    loadBar.increase()
    # Current High Low
    c0Hi = lightConfig["npn_current_good"] + lightConfig["npn_current_tolerance"]
    c0Lo = lightConfig["npn_current_good"] - lightConfig["npn_current_tolerance"]
    loadBar.increase()
    c1Hi = lightConfig["pnp_high_current_good"] + lightConfig["pnp_high_current_tolerance"]
    c1Lo = lightConfig["pnp_high_current_good"] - lightConfig["pnp_high_current_tolerance"]
    loadBar.increase()
    c2Hi = lightConfig["pnp_low_current_good"] + lightConfig["pnp_low_current_tolerance"]
    c2Lo = lightConfig["pnp_low_current_good"] - lightConfig["pnp_low_current_tolerance"]
    loadBar.increase()
    c3Hi = lightConfig["od_peak_current_good"] + lightConfig["od_peak_current_tolerance"]
    c3Lo = lightConfig["od_peak_current_good"] - lightConfig["od_peak_current_tolerance"]
    loadBar.increase()
    c4Hi = lightConfig["od_peak_current_good"] + lightConfig["od_peak_current_tolerance"]
    c4Lo = lightConfig["od_peak_current_good"] - lightConfig["od_peak_current_tolerance"]
    loadBar.increase()
    currentData = arduino.read_until(b'}')
    loadBar.increase()
    currentData = currentData.decode("UTF-8")
    loadBar.increase()
    current = currentData[:-1]
    loadBar.increase()
    currentlist = current.split(",")
    loadBar.increase()
    #print(currentlist)
    try:
        if int(currentlist[0]) > c0Lo and int(currentlist[0]) < c0Hi:
            pf[0] = True # NPN
        measuredData.npnCurrent = currentlist[0]
        measuredData.contPeak = currentlist[0]
        loadBar.increase()
        if int(currentlist[1]) > c1Lo and int(currentlist[1]) < c1Hi:
            pf[1] = True # PNP hi
        measuredData.pnpHiCurrent = currentlist[1]
        measuredData.analogHi = currentlist[1]
        loadBar.increase()
        if int(currentlist[2]) > c2Lo and int(currentlist[2]) < c2Hi:
            pf[2] = True # PNP lo
        measuredData.pnpLoCurrent = currentlist[2]
        measuredData.analogLo = currentlist[2]
        loadBar.increase()
        if int(currentlist[3]) > c3Lo and int(currentlist[3]) < c3Hi:
            pf[3] = True # NPN OD
        loadBar.increase()
        if int(currentlist[4]) > c4Lo and int(currentlist[4]) < c4Hi:
            pf[4] = True # PNP OD
            measuredData.odPeak = currentlist[4]
        loadBar.increase()
    except:
        pf = [False, False, False, False, False]
        loadBar.increase()
    #print(currentlist)
    measuredData.currentPf = pf
    
    time.sleep(0.5)
    loadBar.increase()
    arduino.reset_input_buffer()
    loadBar.increase()
    results = [currentlist, pf]
    loadBar.increase()
    return results

if __name__ == "__main__":
    ## Non-Reused Code ##
    connect()
    documentPath = "C:/Users/SVL226/Documents/EOLTester"
    ## Reused Code ##
    # Main Definitions #
    noPic = None
    print("running")
    lightConfig = loadConfig("JWL150-MD-WHI")
    systemConfig = loadConfig("system_setup")

    configs = [lightConfig, systemConfig]

    try:
        intensityImg, beamImg = Capture("M", 34000, systemConfig)
        images = [intensityImg, beamImg]
    except Exception as e:
        print(e)
        if e == "NoCntrlr":
            noPic = True
        elif e == "noPic":
            noPic = True
        elif e == UnboundLocalError:
            noPic = True
        else:
            noPic = True

    if noPic == False or noPic == None:
        print("Picture Passed")
        try:
            LUTBeamImage, results = beamMeasure(beamImg, configs)
            print(results)
        except Exception as e:
            print(e)
        try:
            results = intensityMeasure(images, configs)
            print(results)
        except Exception as e:
            print(e)
        try:
            results = currentMeasure(lightConfig)
            print(results)
        except Exception as e:
            print(e)
        cv2.imshow("beam", LUTBeamImage)
        cv2.imshow("intensity", intensityImg)
        while True:
            if cv2.waitKey(0) & 0xff == ord('q'):
                break
    else:
        print("No Picture Passed")
        try:
            results = currentMeasure(lightConfig)
            print(results)
        except Exception as e:
            print(e)
