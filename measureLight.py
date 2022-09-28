from vimba import *
import cv2
import numpy as np
import matplotlib.pyplot as plt
import datetime
from array import *
import lut
import json

def capture(light): #Captures Image and Performs Background Subtraction
    settingsfile = light + "Settings.xml"
    try:
        with Vimba.get_instance() as vimba:
            cams = vimba.get_all_cameras()
            with cams[0] as cam:
                cam.load_settings(settingsfile)

                frame = cam.get_frame()
                bgImage = frame.as_opencv_image()
                frame = cam.get_frame()
                fgImage = frame.as_opencv_image()
                test = False
    except:
        image = cv2.imread("test_1.PNG")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        test = True
    
    #ToDo: Back Ground Subtraction, fgImage - bgImage = image. How To With OpenCV?

def measure_light(light):

    # Import Config File
    filePath = "configs/"+light+".json"
    with open(filePath, 'r') as file:
        data = json.load(file)

    try:
        # Initialize Vimba Instance
        with Vimba.get_instance() as vimba:
            # Connect to Camera
            cams = vimba.get_all_cameras()
            with cams[0] as cam:
                # Load Camera Settings
                cam.load_settings("colorSetting.xml", PersistType.All)

                # Obtain Frame, Convert to Mono, Convert to OpenCV Image
                frame = cam.get_frame()
                frame.convert_pixel_format(PixelFormat.Mono8)
                image = frame.as_opencv_image()
                test = False
    except:
        image = cv2.imread("test_1.PNG")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        test = True

    # Grab Lut Exported From Zemax
    zemaxLut = lut.finalLut

    # Set Uniformity Value
    uniformityValue = 255*0.8
    # Set Pass/Fail Thresholds
    # - Intensity
    intensityHigh = data['intensityHigh']
    intensityLow = data['intensityLow']
    # - Symmetry
    symmetryGap = data['symmetry_gap']
    #symmetryLow = data['symmetryLow']
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

    # Create a Bianary Array, Where Pixels Within The 80% Uniformity Are 1, And Those Outside Are 0.
    # Essentially This is Blob Detection
    ret,thresh = cv2.threshold(filteredImage,uniformityValue,255,0)

    # Calculate The Moments of The Bianary Image
    M = cv2.moments(thresh)

    # Calculate X,Y Co-ordinates of Blob Centroid
    try:
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
    except:
        # No Moments Found, Set cX and cY to None
        cX = None
        cY = None

    # If Blob is found: Continue Code, Else: Display Image
    if cX != None:

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
                    flux = flux + image[row-1][col-1]
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
                    horizontal_profile[x-1] = image[cY][x_end-1]
                    x_end = x_end - 1
                    x=x+1

            # Copy data from image into Vertical Profile
            x = 0
            if y_end != 0:
                while y_end >= y_start:
                    vertical_profile[x-1] = image[y_end-1][cX]
                    y_end = y_end - 1
                    x=x+1

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
            figure, axis = plt.subplots(1, 2)
            horiz_x = np.array(range(maxVal_2-minVal))
            horiz_y = horizontal_profile
            vert_x = np.array(range(otherIndex[0][-1]-otherIndex[0][0]))
            vert_y = vertical_profile
            axis[0].plot(horiz_x, horiz_y, color = "red")
            axis[0].set_title("Horizontal Profile")
            axis[1].plot(vert_x, vert_y, color = "blue")
            axis[1].set_title("Vertical Profile")

            # Setup Text Additions 
            # - Pass/Fail values
            cv2.putText(image, "I: " + str(intensityLow) + ", " + str(intensityHigh) + ", " + str(flux), (34,35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2) #Total Flux
            cv2.putText(image, "S: " + str(symmetryLow) + ", " + str(symmetryHigh) + ", " + str(cY), (25,70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2) #Beam Symmetry
            cv2.putText(image, "x: " + str(xLow) + ", " + str(xHigh) + ", " + str(horiz_length), (25,105), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2) #X value - 80% Uniformity Size
            cv2.putText(image, "y: " + str(yLow) + ", " + str(yHigh) + ", " + str(vert_length), (25,140), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2) #Y value - 80% Uniformity Size
            # - Light P/N + Family
            PN = data["light"] + "-" + str(data["size"]) + "-" + data["color"]
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
            #ToDo: Create a symmetry test
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
            
            if test == True:
                cv2.putText(image, "TEST IMAGE", (150,440), cv2.FONT_HERSHEY_SIMPLEX, 5, (0,0,0), 6)
    return image, horiz_x, horiz_y, vert_x, vert_y




