from vimba import *
import cv2
import numpy as np
import datetime
from array import *
import lut
import json
import serial
import time

arduino = serial.Serial('COM8', 9600)
time.sleep(1)
ready = arduino.read_all()
print(ready)

def capture(light, lightColor, exp): #Captures Image, Performs Background Subtraction, Determines Test Mode
    try:
        with Vimba.get_instance() as vimba:
            cams = vimba.get_all_cameras()
            print('cams obtained')
            #print(exp)
            with cams[0] as cam:
                print('cams[0] found')
                cam.load_settings("colorSettings.xml", PersistType.All)
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

def CaptureExt(exp):

    print("in CaptureExt()")
    #msg = 'C' + str(exp)
    #print(msg)
    #msgbyte = bytes(msg, 'utf-8')
    #print(msgbyte)
    #arduino.write(msgbyte)
    print("written to arduino")
    with Vimba.get_instance() as vimba:
        cams = vimba.get_all_cameras()
        with cams[0] as cam:
            print('cam[0] found')
            msg = 'C100'
            msgbyte = bytes(msg, 'utf-8')
            arduino.write(msgbyte)
            try:
                frame = cam.get_frame()
                frame.convert_pixel_format(PixelFormat.Bgr8)
                image = frame.as_opencv_image()
            except:
                print("timeout")
    test = False
    return image, test
#End CaptureExt() 

def loadConfig(light, color, lens):
    filePath = "configs/"+light+"-"+color+"-"+lens+".json"
    try:
        with open(filePath, 'r') as file:
            print("found config")
            data = json.load(file)
    except FileNotFoundError as e:
        return 1

    return data
#End loadConfig()

def measure(light, color, lens):
    # Load Config for Light
    data = loadConfig(light, color, lens)
    
    if data == 1:
        return None

    # Obtain Image
    #image, test = capture(data["light"], data["color"], data["exposure"])
    image, test = CaptureExt(data["exposure"])
    print("received img")
    # Grab Lut Exported From Zemax 
    zemaxLut = lut.finalLut
    
    # Set Uniformity Value 
    uniformityValue = 255*0.8

    ## -- Set Pass/Fail Thresholds From Config -- ##
    # - Intensity
    intensityHigh = data['intensityHigh']
    intensityLow = data['intensityLow']
    # - Symmetry
    symmetryGap = data['symmetry_gap']
    # - X Vlaue
    xHigh = data['xHigh']
    xLow = data['xLow']
    # - Y Value
    yHigh = data['yHigh']
    yLow = data['yLow']

    # Initiate Flux Value
    flux = 0

    # Blur The Image
    filteredImage = cv2.GaussianBlur(image,(15,15),0)
    if test == False:
        print('test false')
        bwImage = cv2.cvtColor(filteredImage, cv2.COLOR_BGR2GRAY)
        print ('converted bwImage')
    # Create a Bianary Array, Where Pixels Within The 80% Uniformity Are 1, And Those Outside Are 0.
    # Essentially This is Blob Detection
    try:
        ret,thresh = cv2.threshold(bwImage,uniformityValue,255,0)
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
        otherIndex = np.where(filteredImage >= uniformityValue)

        # Secondary Check for Blob Presence
        if len(otherIndex[0]) > 0:
            minVal = np.asarray(otherIndex[1]).min()
            maxVal_2 = np.asarray(otherIndex[1]).max()

            midpoint_vertical = int((maxVal_2 + minVal) / 2)
            midpoint_horizontal = int((otherIndex[0][-1] + otherIndex[0][0]) / 2)

            symmetryHigh = int(midpoint_horizontal+(symmetryGap/2))
            symmetryLow = int(midpoint_horizontal-(symmetryGap/2))

            # Calculate total Flux of 80% rectangle
            row = otherIndex[0][0]
            row_max = otherIndex[0][-1]

            while row <= row_max:
                col = minVal
                col_max = maxVal_2
                while col <= col_max:
                    flux = flux + bwImage[row-1][col-1]
                    col = col+1
                row = row+1

            # Define x and y start/end values for cross section profiles
            y_start = otherIndex[0][0]
            y_end = otherIndex[0][-1]
            x_start = minVal
            x_end = maxVal_2

            # Define length of horizontal and vertical cross section array
            horiz_length = maxVal_2-minVal
            vert_length = otherIndex[0][-1]-otherIndex[0][0]
            horizontal_profile = np.arange(horiz_length)
            vertical_profile = np.arange(vert_length)

            # Copy data from image into Horizontal Profile
            x = 0
            if x_end != 0:
                while x_end >= x_start:
                    horizontal_profile[x-1] = bwImage[cY][x_end-1]
                    x_end = x_end - 1
                    x=x+1

            # Copy data from image into Vertical Profile
            x = 0
            if y_end != 0:
                while y_end >= y_start:
                    vertical_profile[x-1] = bwImage[y_end-1][cX]
                    y_end = y_end - 1
                    x=x+1

            if test == True:
                #Convert Image to RGB
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

            #Apply Custom LUT
            image = cv2.LUT(image, zemaxLut)

            #Draw 80% Box
            cv2.rectangle(image, (minVal, otherIndex[0][0]), (maxVal_2, otherIndex[0][-1]),
                (255, 255, 255), 2)
            # Draw Cross Section Lines For Visual Feedback
            cv2.line(image, (cX, otherIndex[0][0]), (cX, otherIndex[0][-1]) ,(0, 0, 0), 2)
            cv2.line(image, (minVal, cY), (maxVal_2, cY), (0, 0, 0), 2)

            #Draw Center of 80% Rectangle and Label
            cv2.circle(image, (midpoint_vertical, midpoint_horizontal), 5, (0,0,0), -1)
            cv2.putText(image, "box center", (midpoint_vertical - 25, midpoint_horizontal - 25),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)

            # Draw Centroid of Beam and Label
            cv2.circle(image, (cX, cY), 5, (0,0,0), -1)
            cv2.putText(image, "centroid", (cX - 25, cY - 25),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)

            # Arrange and plot cross section data using MatPlotLib
            horiz_x = np.array(range(maxVal_2-minVal))
            horiz_y = horizontal_profile
            vert_x = np.array(range(otherIndex[0][-1]-otherIndex[0][0]))
            vert_y = vertical_profile

            horiz = [horiz_x, horiz_y]
            vert = [vert_x, vert_y]

            # Setup Text Additions 
            # - Pass/Fail values
            cv2.putText(image, "I: " + str(intensityLow) + ", " + str(intensityHigh) + ", " + str(flux), (34,35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2) #Total Flux
            cv2.putText(image, "S: " + str(symmetryLow) + ", " + str(symmetryHigh) + ", " + str(cY), (25,70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2) #Beam Symmetry
            cv2.putText(image, "x: " + str(xLow) + ", " + str(xHigh) + ", " + str(horiz_length), (25,105), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2) #X value - 80% Uniformity Size
            cv2.putText(image, "y: " + str(yLow) + ", " + str(yHigh) + ", " + str(vert_length), (25,140), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2) #Y value - 80% Uniformity Size
            # - Light P/N + Family
            PN = data["light"] + str(data["size"]) + "-" + data["color"]
            cv2.putText(image, PN, (1142,35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2) #Light Part Number
            cv2.putText(image, data["light"] + " Family", (1142,60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2) #Light Family(First part of the Part Number) - redundant?
            # - Date & Time
            # -- Obtain date and time
            sysTime = datetime.datetime.now()
            # -- Parse Date and Time Data 
            cv2.putText(image, sysTime.strftime("%Y-%m-%d"), (1150,675), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2) #Date of capture - will update each time the script runs
            cv2.putText(image, sysTime.strftime("%H:%M:%S"), (1192,700), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2) #Time of capture - will update each time the script runs
            # - Add logo on bottom of image
                #todo: Append the long logo to the bottom of the image, size accordingly
                #for now just use text
            cv2.putText(image, "SMART VISION LIGHTS", (25,700), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
            # - Pass/Fail data
            # -- Intensity
            if flux > intensityLow and flux < intensityHigh:
                # Flux Passed
                cv2.putText(image, "PASS", (650,35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2) 
            else:
                # Flux Failed
                cv2.putText(image, "FAIL", (650,35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2) 

            # -- Symmetry
            if cY > symmetryLow and cY < symmetryHigh:
                # Symmetry Passed
                cv2.putText(image, "PASS", (650,70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2) 
            else:
                # Symmetry Failed
                cv2.putText(image, "FAIL", (650,70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2) 

            # -- X Value
            if horiz_length > xLow and horiz_length < xHigh:
                # X Passed
                cv2.putText(image, "PASS", (650,105), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2) 
            else:
                # X Failed
                cv2.putText(image, "FAIL", (650,105), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2) 

            # -- Y Value
            if vert_length > yLow and vert_length < yHigh:
                # Y Passed
                cv2.putText(image, "PASS", (650,140), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2) 
            else:
                # Y Failed
                cv2.putText(image, "FAIL", (650,140), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        result = arduino.read_all()
        result = result.decode()           
    else:
        print("blob not found")
        if test == True:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        image = cv2.LUT(image, zemaxLut)
        horiz = [1, 2]
        horiz[0] = np.arange(1,11)
        horiz[1] = 2 * horiz[0] + 5
        vert = horiz
        if test == True:
                cv2.putText(image, "TEST IMAGE", (150,440), cv2.FONT_HERSHEY_SIMPLEX, 5, (0,0,0), 6)
        flux = cY = horiz_length = vert_length = 0 
        
        time.sleep(1.5)
        result = arduino.read_all()
        result = result.decode()
        passFail = [flux, cY, horiz_length, vert_length]
        time.sleep(0.5)
        arduino.reset_input_buffer()
    return image, horiz, vert, result #passFail
#End measure()