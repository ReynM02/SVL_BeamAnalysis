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
alvium = 0.75  # 2

arduino = serial.Serial()
arduino.baudrate = 19200

documentPath = ""

def connect():
    readyString = ""
    ports, pnum = fp.run()
    x=0
    #print(ports, pnum)
    while x < pnum:
        print(x)
        arduino.port = ports[x]
        #print(ports[x])
        arduino.open()
        time.sleep(2)
        if arduino.is_open:
            ready = arduino.read_all()
            try:
                readyString = ready.decode("UTF-8")
            except:
                readyString = "not matching baudrate"
            #print(readyString)
        if readyString == 'SLA':
            #print("found it")
            return 1
        else:
            arduino.close()
            x += 1

        
def capture(light, lightColor, exp): #Captures Image, Performs Background Subtraction, Determines Test Mode
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
#End Capture()

def unwarpImg(img, src, dst):
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
    print("in FFC")
    flatImg = cv2.imread("FlatImg.bmp")
    darkImg = cv2.imread("DarkImg.bmp")

    flatImg = cv2.cvtColor(flatImg, cv2.COLOR_BGR2GRAY)
    darkImg = cv2.cvtColor(darkImg, cv2.COLOR_BGR2GRAY)

    fdImg = flatImg-darkImg
    m = np.average(fdImg)
    
    correctedImg = np.asarray(( ( rawImg - darkImg ) * m ) / (flatImg - darkImg), dtype=np.uint8)

    return correctedImg

def CaptureExt(cam, mode, exp, config):
    print("in CaptureExt()")
    print('cam[0] found')
    expTime = cam.ExposureTime
    print('exp calc')
    expTime.set(exp)
    print("exp set")
    msg = str(mode) + str(exp)
    print("msg created")
    msgbyte = bytes(msg, 'utf-8')
    print(msgbyte)
    print("msg converted to byte")
    arduino.write(msgbyte)
    print("msg sent to arduino")
    hs = None
    print("read duino")
    try:
        while hs != b'S':
            print("in loop")
            hs = arduino.read(1)
        try:
            bgframe = cam.get_frame(timeout_ms=int(exp+100))
            print("got bgframe")
            bgframe.convert_pixel_format(PixelFormat.Bgr8)
            print("converted frame")
            bgimage = bgframe.as_opencv_image()
            print("saved as bgimage")
            arduino.write(bytes("K", 'utf-8'))
        except:
            print("timeout")
            arduino.write(bytes("K", 'utf-8'))
            raise Exception("NoPic")

        hs = None
        while hs != b'S':
            hs = arduino.read(1)
        try:
            frame = cam.get_frame(timeout_ms=5000)
            print("got frame")
            frame.convert_pixel_format(PixelFormat.Bgr8)
            print("converted frame")
            image = frame.as_opencv_image()
            print("image saved as image")
            arduino.write(bytes("K", 'utf-8'))
        except:
            print("timeout2 - continue anyway")
            arduino.write(bytes("K", 'utf-8'))
        test = False
    except:
        arduino.write(bytes("K", 'utf-8'))
        arduino.write(bytes("K", 'utf-8'))  
    try:
        image = image - bgimage
    except:
        return None, None, True
    #image = flatFieldCorrection(image)
    print("bg sub done")
    src = np.float32(config["src"])
    dst = np.float32(config["dst"])
    unwarped = unwarpImg(image, src, dst)
    print("unwarped image")
    beamImg = unwarped #cv2.GaussianBlur(unwarped, (15,15), 0)
    maxVal = int(beamImg.max())
    beamImg = np.float32(beamImg/int(maxVal))
    beamImg = beamImg * 255
    beamImg = beamImg.astype(np.uint8)
    return unwarped, beamImg, test
#End CaptureExt() 

def loadConfig(light_string):
    filePath = documentPath + "/configs/" + light_string + ".json"
    try:
        with open(filePath, 'r') as file:
            print("found config")
            data = json.load(file)
    except FileNotFoundError:
        return 1

    return data
#End loadConfig()

def measure(light_string, cam):
    # Load Config for Light
    data = loadConfig(light_string)
    config = loadConfig("system_setup")
    # Get Light Mode from Config
    mode = data['mode']
    
    if data == 1:
        return None

    # Obtain Image
    #image, test = capture(data["light"], data["color"], data["exposure"])
    image, beamImg, test = CaptureExt(cam, mode, data["exposure"], config)
    print("received img")
    # Grab Lut Exported From Zemax 
    zemaxLut = lut.finalLut
    
    # Set Uniformity Value 
    uniformityValue = 255*0.8  #80%

    ## -- Set Pass/Fail Thresholds From Config -- ##
    # - Intensity
    intensityHigh = data['flux_good'] + data["flux_tolerance"]
    intensityLow = data['flux_good'] - data["flux_tolerance"]
    # - Symmetry
    symmetryGap = data['symmetry_tolerance']
    # - X Vlaue
    xHigh = data['x_good'] + data["x_tolerance"]
    xLow = data['x_good'] - data["x_tolerance"]
    # - Y Value
    yHigh = data['y_good'] + data["y_tolerance"]
    yLow = data['y_good'] - data["y_tolerance"]

    # Initiate Flux Value
    flux = 0
    lux = 0

    # Blur The Image
    if test == False:
        print('test false')
        bwBeamImg = cv2.cvtColor(beamImg, cv2.COLOR_BGR2GRAY)
        lightColor = data["color"]
        if lightColor == "WHI":
            bwImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            b, g, r = cv2.split(image)
            if lightColor == "470":
                bwImage = b
            elif lightColor == "530":
                bwImage = g
            elif lightColor == "625":
                bwImage = r
            else:
                bwImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        print ('converted bwImage')
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
    except:
        # No Moments Found, Set cX and cY to None
        cX = None
        cY = None
        print('no moments found')

    # If Blob is found: Continue Code, Else: Display Image
    if cX != None:
        print("blob found")
        # Create an Array of Pixel Locations (x,y) For Pixels With an Intensity
        # Greater Than or Equal to uniformityValue  
        uniformityIndex = np.where(beamImg >= uniformityValue)
        
        # Secondary Check for Blob Presence
        if len(uniformityIndex[0]) > 0:
            minVal = np.asarray(uniformityIndex[1]).min()
            maxVal_2 = np.asarray(uniformityIndex[1]).max()

            midpoint_vertical = int((maxVal_2 + minVal) / 2)
            midpoint_horizontal = int((uniformityIndex[0][-1] + uniformityIndex[0][0]) / 2)

            luxHorizontal = np.arange(midpoint_horizontal-int(config["center_lux_size"]), midpoint_horizontal+int(config["center_lux_size"]))
            luxvertical = [midpoint_vertical-int(config["center_lux_size"]), midpoint_vertical+int(config["center_lux_size"])]
            luxBox = luxHorizontal
            while luxvertical[0]+1 < luxvertical[1]:
                luxBox = np.vstack((luxBox, luxHorizontal))
                luxvertical[0] = luxvertical[0]+1

            luxMinVal = np.asarray(luxBox[1]).min()
            luxMaxVal = np.asarray(luxBox[1]).max()

            luxHigh = data["lux_good"] + data["lux_tolerance"]
            luxLow = data["lux_good"] - data["lux_tolerance"]

            symmetryHigh = int(midpoint_horizontal+(symmetryGap/2))
            symmetryLow = int(midpoint_horizontal-(symmetryGap/2))

            # Calculate total Flux of 80% rectangle
            row = uniformityIndex[0][0]
            row_max = uniformityIndex[0][-1]
            luxRow = luxBox[0][0]
            luxRow_Max = luxBox[0][-1]
             
            while row <= row_max:
                col = minVal
                col_max = maxVal_2
                while col <= col_max:
                    flux = flux + bwImage[row-1][col-1]
                    col = col+1
                row = row+1
            
            while luxRow <= luxRow_Max:
                col = luxMinVal
                col_max = luxMaxVal
                while col <= col_max:
                    lux = lux + bwImage[row-1][col-1]
                    col = col+1
                luxRow = luxRow+1

            nonbiasLux = int(lux / int(data["exposure"]))

            finalLux = nonbiasLux * int(config["lux_calibration"])

            # Define x and y start/end values for cross section profiles
            y_start = uniformityIndex[0][0]
            y_end = uniformityIndex[0][-1]
            x_start = minVal
            x_end = maxVal_2

            # Define length of horizontal and vertical cross section array
            horiz_length = int((maxVal_2-minVal) / config["ppm_calibration"])
            vert_length = int((uniformityIndex[0][-1]-uniformityIndex[0][0]) / config["ppm_calibration"]) 
            horizontal_profile = np.arange(maxVal_2-minVal)
            vertical_profile = np.arange(uniformityIndex[0][-1]-uniformityIndex[0][0])

            # Copy data from image into Horizontal Profile
            x = 0
            if x_end != 0:
                while x_end > x_start:
                    print(x_end)
                    x=x+1
                    print(x-1)
                    horizontal_profile[(x-1)] = bwImage[cY][x_end-1]
                    x_end = x_end - 1


            # Copy data from image into Vertical Profile
            x = 0
            if y_end != 0:
                while y_end >= y_start:
                    vertical_profile[x-1] = bwImage[y_end-1][cX]
                    y_end = y_end - 1
                    x=x+1

            if test == True:
                #Convert Image to RGB
                bwImage = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

            rgbBeamImg = cv2.cvtColor(bwBeamImg, cv2.COLOR_GRAY2RGB)
            #Apply Custom LUT
            rgbBeamImg = cv2.LUT(rgbBeamImg, zemaxLut)

            #Draw 80% Box
            cv2.rectangle(rgbBeamImg, (minVal, uniformityIndex[0][0]), (maxVal_2, uniformityIndex[0][-1]),
                (255, 255, 255), 2)
            # Draw Cross Section Lines For Visual Feedback
            cv2.line(rgbBeamImg, (cX, uniformityIndex[0][0]), (cX, uniformityIndex[0][-1]) ,(0, 0, 0), 2)
            cv2.line(rgbBeamImg, (minVal, cY), (maxVal_2, cY), (0, 0, 0), 2)

            #Draw Center of 80% Rectangle and Label
            cv2.circle(rgbBeamImg, (midpoint_vertical, midpoint_horizontal), 5, (0,0,0), -1)
            cv2.putText(rgbBeamImg, "box center", (midpoint_vertical - 25, midpoint_horizontal - 25),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)

            # Draw Centroid of Beam and Label
            cv2.circle(rgbBeamImg, (cX, cY), 5, (0,0,0), -1)
            cv2.putText(rgbBeamImg, "centroid", (cX - 25, cY - 25),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)

            # Arrange and plot cross section data using MatPlotLib
            horiz_x = np.array(range(maxVal_2-minVal))
            horiz_y = horizontal_profile
            vert_x = np.array(range(uniformityIndex[0][-1]-uniformityIndex[0][0]))
            vert_y = vertical_profile

            horiz = [horiz_x, horiz_y]
            vert = [vert_x, vert_y]

            # - Pass/Fail data
            pf = [False, False, False, False, False, False, False, False, False]
            # -- Flux
            if flux > intensityLow and flux < intensityHigh:
                # Flux Passed
                pf[0] = True

            # -- LUX
            if finalLux > luxLow and finalLux < luxHigh:
                pf[1] = True

            # -- Symmetry
            if cY-midpoint_vertical < symmetryGap and cX-midpoint_horizontal < symmetryGap:
                # Symmetry Passed
                pf[2] = True

            # -- X,Y Value
            if horiz_length > xLow and horiz_length < xHigh and vert_length > yLow and vert_length < yHigh:
                # X Passed
                pf[3] = True 

        # Current High Low
        c0Hi = data["npn_current_good"] + data["npn_current_tolerance"]
        c0Lo = data["npn_current_good"] - data["npn_current_tolerance"]
        
        c1Hi = data["pnp_high_current_good"] + data["pnp_high_current_tolerance"]
        c1Lo = data["pnp_high_current_good"] - data["pnp_high_current_tolerance"]

        c2Hi = data["pnp_low_current_good"] + data["pnp_low_current_tolerance"]
        c2Lo = data["pnp_low_current_good"] - data["pnp_low_current_tolerance"]

        c3Hi = data["od_peak_current_good"] + data["od_peak_current_tolerance"]
        c3Lo = data["od_peak_current_good"] - data["od_peak_current_tolerance"]

        c4Hi = data["od_peak_current_good"] + data["od_peak_current_tolerance"]
        c4Lo = data["od_peak_current_good"] - data["od_peak_current_tolerance"]

        symGood = [cX-midpoint_horizontal, cY-midpoint_vertical]
        time.sleep(1.5)
        currentData = arduino.read_until(b'}')
        currentData = currentData.decode("UTF-8")
        current = currentData[:-1]
        currentlist = current.split(",")
        if int(currentlist[0]) > c0Lo and int(currentlist[0]) < c0Hi:
            pf[4] = True
        if int(currentlist[1]) > c1Lo and int(currentlist[1]) < c1Hi:
            pf[5] = True
        if int(currentlist[2]) > c2Lo and int(currentlist[2]) < c2Hi:
            pf[6] = True
        if int(currentlist[3]) > c3Lo and int(currentlist[3]) < c3Hi:
            pf[7] = True
        if int(currentlist[4]) > c4Lo and int(currentlist[4]) < c4Hi:
            pf[8] = True
        print(currentlist)
        results = [flux, finalLux, cY, cX, horiz_length, vert_length]
        results.extend(currentlist)
        time.sleep(0.5)
        arduino.reset_input_buffer()          
    else:
        symGood = [0, 0]
        pf = [False, False, False, False, False, False, False, False, False]
        print("blob not found")
        image = cv2.imread("C:/Users/matt.reynolds/OneDrive - Smart Vision Lights/Desktop/SVL_BeamAnalysis/src/SVLLogoPNG.png")
        try:
            rgbBeamImg = cv2.cvtColor(bwBeamImg, cv2.COLOR_GRAY2RGB)
            rgbBeamImg = cv2.LUT(rgbBeamImg, zemaxLut)
        except:
            rgbBeamImg = image
        horiz = [1, 2]
        horiz[0] = np.arange(1,11)
        horiz[1] = 2 * horiz[0] + 5
        vert = horiz
        #if test == True:
                #cv2.putText(rgbBeamImg, "TEST IMAGE", (150,440), cv2.FONT_HERSHEY_SIMPLEX, 5, (0,0,0), 6)
        flux = finalLux = cY = cX = horiz_length = vert_length = 0 
        #time.sleep(1.5)
        currentData = arduino.read_until(b'}')
        currentData = currentData.decode("UTF-8")
        current = currentData[:-1]
        currentlist = current.split(",")        
        print(currentlist)
        results = [flux, finalLux, cY, cX, horiz_length, vert_length]
        results.extend(currentlist)
        time.sleep(0.5)
        arduino.reset_input_buffer()
    p = alvium
    w = int(rgbBeamImg.shape[1] * p)
    h = int(rgbBeamImg.shape[0] * p)
    if test == False:
        res_img = cv2.resize(rgbBeamImg, (w,h))
        passCount = 0
        for n, _ in enumerate(pf):
            if pf[n] == True:
                passCount += 1
        if passCount == 4:
            passFail = True
        else:
            passFail = False
    else:
        res_img = rgbBeamImg
        passCount = 0
        for n, _ in enumerate(pf):
            if pf[n] == True:
                passCount += 1
        if passCount == 4:
            passFail = True
        else:
            passFail = False
        symGood = None
    return res_img, horiz, vert, results, symGood, pf, passFail
#End measure()

#### DEBUG MODE ####
#with Vimba.get_instance() as vimba:
    cams = vimba.get_all_cameras()
    cams[0].set_access_mode(AccessMode.Full)
    with cams[0] as cam:
        documentPath = "C:/Users/SVL226/Documents/EOLTester"
        path = documentPath + "/src/EOLTestSettings.xml"
        cam.load_settings(path, PersistType.NoLUT)
        connect()
        measure("JWL150-MD-WHI", cam)