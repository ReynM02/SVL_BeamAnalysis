
import PySimpleGUI as sg
import cv2
import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import measureLight as SLA # Smart Light Analyzer
import datetime
import psutil
import time
import os
import pyautogui
from csv import writer
import numpy as np
from vimba import *

# Pack the Graphs from MatPlotLib to TKinter
def pack_figure(graph, figure):
    canvas = FigureCanvasTkAgg(figure, graph.Widget)
    plot_widget = canvas.get_tk_widget()
    plot_widget.pack(side='top', fill='both', expand=1)
    return plot_widget

# Cleans and Plots the Graphs
def plot_figure(index, x, y):
    fig = plt.figure(index)         # Select Graph to Change
    ax = plt.gca()                  # Get the current graph
    ax.cla()                        # Clear the current graph
    if index == 1:                     
        ax.set_title("Horizontal Profile")  # Set Titles for Graphs
    else:
        ax.set_title("Vertical Profile")
    plt.plot(x, y)                  # Plot y versus x as lines and/or markers
    fig.canvas.draw()               # Re-Draws Graph 

def append_list_as_row(file_name, list_of_elem):
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)

fig1 = plt.figure(1)                # Create a new figure
ax1 = plt.subplot(111)              # Add a subplot to the current figure
fig2 = plt.figure(2)                # Create a new figure
ax2 = plt.subplot(111)              # Add a subplot to the current figure

sg.theme("SmartVision")

SVLIcon = b'iVBORw0KGgoAAAANSUhEUgAABZYAAAWUCAYAAABSplMMAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAIdUAACHVAQSctJ0AAP'

SVLStack = b'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'

buttons = [
    [sg.Button("Exit", size=(10, 1))],
    [sg.Button("JWL", size =(10, 1))],
    [sg.Button("LSR", size =(10, 1))]
]

lights = [
    'LSR',
    'JWL'
]

linear_size = [
    '150',
    '300',
    '450',
    '600'
]

lens_config = [
    'S',
    'N',
    'W'
]

other_size = [
    '150',
    '225'
]

colors = [
    'WHI',
    '625',
    '470'
]

lists = [
    [sg.Combo(lights, default_value='LSR', key="-LIGHT-", enable_events=True),
        sg.Combo(lens_config, default_value='S', key="-LENS-", enable_events=True)],
    [sg.Combo(linear_size, default_value='300', key="-SIZE-", enable_events=True)],
    [sg.Combo(colors, default_value='WHI', key="-COLORS-")]
]

image_column = [
    [sg.Text("EOL Tester", size=(30, 1), text_color="#134A8F", justification="center", font=["Kanit",48,"bold"], expand_x= True)],
    [sg.Image(filename="", key="-IMAGE-", size=(80, 80), expand_x=True, expand_y=True, background_color="#ffffff")],
    [sg.Text("Light P/N:", font=["Open Sans",15,""]), sg.InputText(enable_events=True, size=(20, 5), font=["",15,""], key="-LIGHT_STRING-", do_not_clear=True)],
    [sg.Text("Light S/N:", font=["Open Sans",15,""]), sg.InputText(enable_events=True, size=(20, 5), font=["",15,""], key="-SERIAL_NUM-", do_not_clear=True)],
    [sg.Button("Measure", size=(10,2), font=["Open Sans",20,"bold"], key="-MEASURE-")]
]

graph_column = [
    [sg.Text("Graph Analysis", font=["Kanit",32,"bold"], size=(10, 1), justification="center", expand_x= True),
        sg.Button("Report", size=(10,1), font=["Open Sans",10,"bold"], key="-SHWRPRT-")],
    [sg.Graph((200, 100), (0, 0), (200, 100), key="Graph1", expand_x=True)],
    [sg.Graph((200, 100), (0, 0), (200, 100), key="Graph2", expand_x=True)]
]

#    [sg.Graph((200, 100), (0, 0), (200, 100), key="Graph1", expand_x=True)],
#    [sg.Graph((200, 100), (0, 0), (200, 100), key="Graph2", expand_x=True)]

report_column = [
    [sg.Text("Measurements", font=["Kanit",32,"bold"], size=(10, 1), justification="center", expand_x= True),
         sg.Button("Graphs", size=(10,1), font=["Open Sans",10,"bold"], key="-SHWGRPH-")],
    [sg.Text("Test Station #1", font=["Kanit",20,"bold"], size=(10, 1), justification="left", expand_x= True),
        sg.Text("Time Measured", font=["Kanit",15,"bold"], size=(10, 1), justification="right", expand_x= True, key="-TIME-", border_width=1)],
    [sg.HorizontalSeparator()],
    [sg.Text("BR100-LI-GHT\nSVL123456", font=["Kanit",15,"bold"], size=(35, 2), justification="left", expand_x=True, key="-PNSN-"),
        sg.Text("Status:", font=["Open Sans",15,"bold"], size=(7, 1), justification="right"),
        sg.Text("FAIL", text_color="red", font=["Open Sans",20,"bold"], size=(4, 1), justification="center", relief="solid", border_width=1, key="-STATUS-")],
    [sg.Text("Total Flux:", font=["Open Sans",15,"bold"], size=(17, 1), justification="right", expand_x=True, key="-TINTENSITY-"),
        sg.Text("99999999", font=["Open Sans",15,""], size=(10, 1), justification="center", expand_x= True, key="-FLXMZRD-"),
        sg.Text("99999999±999", font=["Open Sans",15,""], size=(15, 1), justification="center", expand_x= True, key="-FLXHL-"),
        sg.Text("PASS", font=["Open Sans",15,"bold"], size=(10, 1), justification="Left", text_color="green", expand_x= True, key="-FLXPF-")],
    [sg.Text("Center Lux:", font=["Open Sans",15,"bold"], size=(17, 1), justification="right", expand_x= True, key="-CINTENSITY-"),
        sg.Text("Lux", font=["Open Sans",15,""], size=(10, 1), justification="center", expand_x= True, key="-LXMZRD-"),
        sg.Text("999999±999", font=["Open Sans",15,""], size=(15, 1), justification="center", expand_x= True, key="-LXHL-"),
        sg.Text("PASS", font=["Open Sans",15,"bold"], size=(10, 1), justification="Left", text_color="green", expand_x= True, key="-LXPF-")],
    [sg.Text("Symmetry:", font=["Open Sans",15,"bold"], size=(17, 1), justification="right", expand_x= True),
        sg.Text("(10,10)", font=["Open Sans",15,""], size=(10, 1), justification="center", expand_x= True, key="-SYMMZRD-"),
        sg.Text("(99±9,99±9)", font=["Open Sans",15,""], size=(15, 1), justification="center", expand_x= True, key="-SYMHL-"),
        sg.Text("PASS", font=["Open Sans",15,"bold"], size=(10, 1), justification="Left", text_color="green", expand_x= True, key="-SYMPF-")],
    [sg.Text("Beam Size:", font=["Open Sans",15,"bold"], size=(17, 1), justification="right", expand_x= True),
        sg.Text("(500,600)", font=["Open Sans",15,""], size=(10, 1), justification="center", expand_x= True, key="-SZMZRD-"),
        sg.Text("(999±99,999±99)", font=["Open Sans",15,""], size=(15, 1), justification="center", expand_x= True, key="-SZHL-"),
        sg.Text("PASS", font=["Open Sans",15,"bold"], size=(10, 1), justification="Left", text_color="green", expand_x= True, key="-SZPF-")],
    [sg.Text("Peak Current(Cont.):", font=["Open Sans",15,"bold"], size=(17, 1), justification="right", expand_x= True),
        sg.Text("200mA", font=["Open Sans",15,""], size=(10, 1), justification="center", expand_x= True, key="-PCRNTMZRD-"),
        sg.Text("999±99", font=["Open Sans",15,""], size=(15, 1), justification="center", expand_x= True, key="-PCRNTHL-"),
        sg.Text("PASS", font=["Open Sans",15,"bold"], size=(10, 1), justification="Left", text_color="green", expand_x= True, key="-PCRNTPF-")],
    [sg.Text("Peak Current(OD):", font=["Open Sans",15,"bold"], size=(17, 1), justification="right", expand_x= True),
        sg.Text("200mA", font=["Open Sans",15,""], size=(10, 1), justification="center", expand_x= True, key="-PCRNTOMZRD-"),
        sg.Text("999±99", font=["Open Sans",15,""], size=(15, 1), justification="center", expand_x= True, key="-PCRNTOHL-"),
        sg.Text("PASS", font=["Open Sans",15,"bold"], size=(10, 1), justification="Left", text_color="green", expand_x= True, key="-PCRNTOPF-")],
    [sg.Text("NPN Current:", font=["Open Sans",15,"bold"], size=(17, 1), justification="right", expand_x= True),
        sg.Text("200mA", font=["Open Sans",15,""], size=(10, 1), justification="center", expand_x= True, key="-NPNCRNTMZRD-"),
        sg.Text("999±99", font=["Open Sans",15,""], size=(15, 1), justification="center", expand_x= True, key="-NPNCRNTHL-"),
        sg.Text("PASS", font=["Open Sans",15,"bold"], size=(10, 1), justification="Left", text_color="green", expand_x= True, key="-NPNCRNTPF-")],
    [sg.Text("PNP Current(10v):", font=["Open Sans",15,"bold"], size=(17, 1), justification="right", expand_x= True),
        sg.Text("200mA", font=["Open Sans",15,""], size=(10, 1), justification="center", expand_x= True, key="-PNPHIMZRD-"),
        sg.Text("999±99", font=["Open Sans",15,""], size=(15, 1), justification="center", expand_x= True, key="-PNPHIHL-"),
        sg.Text("PASS", font=["Open Sans",15,"bold"], size=(10, 1), justification="Left", text_color="green", expand_x= True, key="-PNPHIPF-")],
    [sg.Text("PNP Current(5v):", font=["Open Sans",15,"bold"], size=(17, 1), justification="right", expand_x= True),
        sg.Text("200mA", font=["Open Sans",15,""], size=(10, 1), justification="center", expand_x= True, key="-PNPLOMZRD-"),
        sg.Text("999±99", font=["Open Sans",15,""], size=(15, 1), justification="center", expand_x= True, key="-PNPLOHL-"),
        sg.Text("PASS", font=["Open Sans",15,"bold"], size=(10, 1), justification="Left", text_color="green", expand_x= True, key="-PNPLOPF-")],
    [sg.Text("Analog 10v:", font=["Open Sans",15,"bold"], size=(17, 1), justification="right", expand_x= True),
        sg.Text("200mA", font=["Open Sans",15,""], size=(10, 1), justification="center", expand_x= True, key="-AHIMZRD-"),
        sg.Text("999±99", font=["Open Sans",15,""], size=(15, 1), justification="center", expand_x= True, key="-AHIHL-"),
        sg.Text("PASS", font=["Open Sans",15,"bold"], size=(10, 1), justification="Left", text_color="green", expand_x= True, key="-AHIPF-")],
    [sg.Text("Analog 5v:", font=["Open Sans",15,"bold"], size=(17, 1), justification="right", expand_x= True),
        sg.Text("200mA", font=["Open Sans",15,""], size=(10, 1), justification="center", expand_x= True, key="-ALOMZRD-"),
        sg.Text("999±99", font=["Open Sans",15,""], size=(15, 1), justification="center", expand_x= True, key="-ALOHL-"),
        sg.Text("PASS", font=["Open Sans",15,"bold"], size=(10, 1), justification="Left", text_color="green", expand_x= True, key="-ALOPF-")],
]

advanced_column = [
    [sg.Column(report_column, visible=True, key="-REPORT-", expand_x=True, expand_y=True),
        sg.Column(graph_column, visible=False, key="-GRAPHS-", expand_x=True, expand_y=True)]
]

# Define the window layout
layout = [
    [sg.Column(image_column, expand_x=True, expand_y=True),
    sg.pin(sg.Button("R\ne\np\no\nr\nt", font=["Open Sans",10,"bold"], size=(3,7), key="-HIDE-")),
    sg.VSeperator(key="-SEP-"),
    sg.Column(advanced_column, visible=False, key="-ADVNCED-", expand_x=True, expand_y=True)]
]

# Create the window and show it
window = sg.Window('Smart Vision Lights - End Of Line Tester', layout, finalize=True, resizable=True, icon=SVLIcon)
window.maximize()
graph1 = window["Graph1"]
graph2 = window["Graph2"]
plt.ioff()
pack_figure(graph1, fig1)
pack_figure(graph2, fig2)
x = 0
y = 0
plot_figure(1, x, y)
plot_figure(2, x, y)
#Initial Image Holder
window["-IMAGE-"].update(data=SVLStack)
date = datetime.datetime.now()
month, day, year = date.month, date.day, date.year

print(month, day, year)

def hideButtons():
    window["-SHWRPRT-"].update(visible=False)
    window["-SHWGRPH-"].update(visible=False)
    window["-HIDE-"].update(visible=False)
    window["-LIGHT_STRING-"].update(visible=False)
    window["-SERIAL_NUM-"].update(visible=False)
    window["-MEASURE-"].update(visible=False)

def showButtons():
    window["-SHWRPRT-"].update(visible=True)
    window["-SHWGRPH-"].update(visible=True)
    window["-HIDE-"].update(visible=True)
    window["-LIGHT_STRING-"].update(visible=True)
    window["-SERIAL_NUM-"].update(visible=True)
    window["-MEASURE-"].update(visible=True)

def saveReport(hidden, savePath):
    hideButtons()
    window.Refresh()
    if hidden == True:
        window["-ADVNCED-"].update(visible=True)
        window.Refresh()
        image = pyautogui.screenshot()
        showButtons()
        window["-ADVNCED-"].update(visible=False)
        window.Refresh()
    else:
        image = pyautogui.screenshot()
        showButtons()
        window["-ADVNCED-"].update(visible=False)
        window.Refresh()
        window["-ADVNCED-"].update(visible=True)
        window.Refresh()
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    #cv2.imshow("report", image)
    print("saving report")
    written = cv2.imwrite("C:/Users/SVL226/Documents/EOLTester/Reports/Image.jpg", image)
    written = cv2.imwrite(savePath+".jpg", image)
    if written:
        print("image saved")

def main():
    ### --- Main Definitions --- ###
    user_list = psutil.users() # Gets all connected users
    user = user_list[0].name # Gets name of current user
    print(user)
    hidden = True
    savePath = 'C:/Users/' + user + '/Documents/EOLTester'
    SLA.documentPath = savePath
    # Check if save paths are created, create if not created
    if not os.path.exists(savePath):
        os.makedirs(savePath)
    if not os.path.exists(savePath+'/Images'):
        os.makedirs(savePath+'/Images')
    if not os.path.exists(savePath+'/Data'):
        os.makedirs(savePath+'/Data')
    if not os.path.exists(savePath+'/Reports'):
        os.makedirs(savePath+'/Reports')
    SLA.connect() # Connect to the electronics measurment tool
    ### --- Main Loop --- ###
    while True:   
        event, values = window.read(timeout=20) # Reads window actions waiting for inputs
        # event is an action... event == "Exit" is Exit Button being pressed
        if event == "Exit" or event == sg.WIN_CLOSED: # Exit Button Pressed or Window Closed
            break
        elif event == "-HIDE-":
            if hidden == True:
                window['-ADVNCED-'].update(visible=True)
                hidden = False
            else:
                window['-ADVNCED-'].update(visible=False)
                hidden = True
        elif event == "-SHWGRPH-":
                window["-REPORT-"].update(visible=False)
                window["-GRAPHS-"].update(visible=True)
        elif event == "-SHWRPRT-":
                window["-GRAPHS-"].update(visible=False)
                window["-REPORT-"].update(visible=True)
        elif event == "-MEASURE-":
            window['-MEASURE-'].update(disabled=True)
            sysTime = datetime.datetime.now()
            dateString = sysTime.strftime("%Y-%m-%d") + '_' + sysTime.strftime("%H%M%S")
            light_string = values["-LIGHT_STRING-"]
            serialNum = values["-SERIAL_NUM-"]
            splitString = light_string.split('-')
            window["-TIME-"].update(str(sysTime.strftime("%Y-%m-%d") + ' ' + sysTime.strftime("%H:%M:%S")))
            window["-PNSN-"].update(str(light_string + "\n" + serialNum))
            #print(splitString)
            try:
                light = splitString[0]
                mode = splitString[1]
                color = splitString[2]
                invalConfig = False
                if color == "WHI":
                    window["-TINTENSITY-"].update("Total Lux:")
                    window["-CINTENSITY-"].update("Center Lux:")
                else:
                    window["-TINTENSITY-"].update("Total Intensity:")
                    window["-CINTENSITY-"].update("Center Intensity:")
            except IndexError:
                sg.popup('        Error: Invalid Configuration\n Please Re-Enter Light P/N and S/N.', title="Error: InvalConfgErr", modal=True, icon=SVLIcon, font=["Open Sans",20,'bold'])
                print("lightgistics")
                invalConfig = True
            if invalConfig == False:
                try:
                    lens = splitString[3]
                except IndexError:
                    lens = ''
                try:
                    pol = splitString[3]
                except IndexError:
                    pol = ''

                print(light_string)

                try:
                    frame, horiz, vert, results, symGood, pf, passFail = SLA.measure(light_string, cam)
                    data = SLA.loadConfig(light_string)
                    didntRun = False
                except:
                    print("failed")
                    passFail = False
                    didntRun = True

                if didntRun == True:
                    sg.popup('                    Error: Program Error\n Alert Supervisor for Debuging or Try Again.', title="Error: PrgmErr", modal=True, icon=SVLIcon, font=["Open Sans",20,'bold'])
                elif symGood == None:
                    window["-IMAGE-"].update(data=SVLStack)
                    sg.popup('                    Error: No Image Passed\n Alert Supervisor for Debuging or Try Again.', title="Error: ImgErr", modal=True, icon=SVLIcon, font=["Open Sans",20,'bold'])
                else:    
                    plot_figure(1, horiz[0], horiz[1])
                    plot_figure(2, vert[0], vert[1])
                    #frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                    # Update Values for Report Tab


                    imgPath = savePath+"/Images/"
                    #print (os.path.join(imgPath, light_string+'_'+serialNum+'_'+dateString+'.jpg'))
                    isWritten = cv2.imwrite(imgPath+light_string+'_'+serialNum+'_'+dateString+'.jpg', frame)

                    if isWritten:
                        print("image saved")
                    else:
                        print("image not saved")

                    imgbytes = cv2.imencode(".png", frame)[1].tobytes()
                    window["-IMAGE-"].update(data=imgbytes)
                    csvPath = savePath + '/Data/' + str(month) + '-' + str(day) + '-' + str(year) + '_Light_Measurements.csv'
                    rowData = [light_string, serial_num]
                    rowData.extend(results)
                    append_list_as_row(csvPath, rowData)
                    flux = results[0]
                    lux = results[1]
                    cY = results[2]
                    cX = results[3]
                    xLen = results[4]
                    yLen = results[5]
                    npnCurrent = results[6]
                    pnpCurrent10v = results[7]
                    pnpCurrent5v = results[8]
                    odStrobe = results[9]
                  

                    ### - PASS FAIL ASSIGNMENTS - ###
                    # - FLUX OPERATIONS
                    flxMZRDStr = str("{:.1e}".format(flux))
                    window["-FLXMZRD-"].update(flxMZRDStr)
                    if pf[0] == True:
                        window["-FLXPF-"].update("PASS", text_color='green')
                    else:
                        window["-FLXPF-"].update("FAIL", text_color='red')
                    flxHLStr = str("{:.1e}".format(data["flux_good"]))+"±"+str("{:.1e}".format(data["flux_tolerance"]))
                    window["-FLXHL-"].update(flxHLStr)

                    # - LUX OPERATIONS
                    window["-LXMZRD-"].update("{:.1e}".format(lux))
                    if pf[1] == True:
                        window["-LXPF-"].update("PASS", text_color='green')
                    else:
                        window["-LXPF-"].update("FAIL", text_color='red')
                    lxHLStr = str("{:.1e}".format(data["lux_good"]))+"±"+str(data["lux_tolerance"])
                    window["-LXHL-"].update(lxHLStr)

                    # - SYMMETRY OPERATIONS
                    symMZRDStr = "("+str(cX)+","+str(cY)+")"
                    window["-SYMMZRD-"].update(symMZRDStr)
                    if pf[2] == True:
                        window["-SYMPF-"].update("PASS", text_color='green')
                    else:
                        window["-SYMPF-"].update("FAIL", text_color='red')
                    symHLStr = "("+ str(symGood[0]) +","+str(symGood[1])+"±"+str(data["symmetry_tolerance"])+")"
                    window["-SYMHL-"].update(symHLStr)
                    
                    # - BEAM-SIZE OPERATIONS
                    szMZRDStr = "("+str(xLen)+","+str(yLen)+")"
                    window["-SZMZRD-"].update(szMZRDStr)
                    if pf[3] == True:
                        window["-SZPF-"].update("PASS", text_color='green')
                    else:
                        window["-SZPF-"].update("FAIL", text_color='red')
                    szHLStr = "("+ str(data["x_good"]) + "±" + str(data["x_tolerance"]) +","+str(symGood[1])+"±"+str(data["symmetry_tolerance"])+")"
                    window["-SZHL-"].update(szHLStr)

                    # - CURRENT OPERATIONS
                    # High/Low Strings
                    pcrntHLStr = str(data["cont_peak_current_good"]) + "±" + str(data["cont_peak_current_tolerance"])
                    window["-PCRNTHL-"].update(pcrntHLStr)
                    pcrntoHLStr = str(data["od_peak_current_good"]) + "±" + str(data["od_peak_current_tolerance"])
                    window["-PCRNTOHL-"].update(pcrntoHLStr)
                    npncrntHLStr = str(data["npn_current_good"]) + "±" + str(data["npn_current_tolerance"])
                    window["-NPNCRNTHL-"].update(npncrntHLStr)
                    pnphiHLStr = str(data["pnp_high_current_good"]) + "±" + str(data["pnp_high_current_tolerance"])
                    window["-PNPHIHL-"].update(pnphiHLStr)
                    pnploHLStr = str(data["pnp_low_current_good"]) + "±" + str(data["pnp_low_current_tolerance"])
                    window["-PNPLOHL-"].update(pnploHLStr)
                    ahiHLStr = str(data["analog_high_current_good"]) + "±" + str(data["analog_high_current_tolerance"])
                    window["-AHIHL-"].update(ahiHLStr)
                    alowHLStr = str(data["analog_low_current_good"]) + "±" + str(data["analog_low_current_tolerance"])
                    window["-ALOHL-"].update(alowHLStr)
                    # Measured updates
                    window["-PCRNTMZRD-"].update(npnCurrent)    # peak current from cont. mode
                    window["-PCRNTOMZRD-"].update(odStrobe)     # peak current from OD mode
                    window["-NPNCRNTMZRD-"].update(npnCurrent)  # peak current when triggered with NPN line
                    window["-PNPHIMZRD-"].update(pnpCurrent10v) # peak current when triggered with 10v on PNP line
                    window["-PNPLOMZRD-"].update(pnpCurrent5v)  # peak current when triggered with 5v on PNP line
                    window["-AHIMZRD-"].update(npnCurrent)      # peak current when triggered with analog at 10v
                    window["-ALOMZRD-"].update(pnpCurrent5v)    # peak current when triggered with analog at 5v
                    # Pass/Fail
                    if pf[4] == True:
                        window["-NPNCRNTPF-"].update("PASS", text_color='green')
                        window["-PCRNTPF-"].update("PASS", text_color='green')
                        window["-AHIPF-"].update("PASS", text_color='green')
                    else:
                        window["-NPNCRNTPF-"].update("FAIL", text_color='red')
                        window["-PCRNTPF-"].update("FAIL", text_color='red')
                        window["-AHIPF-"].update("FAIL", text_color='red')
                    if pf[5] == True:
                        window["-PNPHIPF-"].update("PASS", text_color='green')
                    else:
                        window["-PNPHIPF-"].update("FAIL", text_color='red')
                    if pf[6] == True:
                        window["-PNPLOPF-"].update("PASS", text_color='green')
                        window["-ALOPF-"].update("PASS", text_color='green')
                    else:
                        window["-PNPLOPF-"].update("FAIL", text_color='red')
                        window["-ALOPF-"].update("FAIL", text_color='red')
                    if pf[7] == True:
                        window["-PCRNTOPF-"].update("PASS", text_color='green')
                    else:
                        window["-PCRNTOPF-"].update("FAIL", text_color='red')
                    
                    if passFail:
                        output = [
                            [sg.Text("", text_color="green", font=["",20,"bold"], justification="center", size=(10, 1))],               
                            [sg.Text("PASS", text_color="green", font=["",50,"bold"], justification="center", size=(10, 1))],
                            [sg.Text(str(rowData))],
                            [sg.OK(size=(10,1), font=["",50,""],p=((15,0),(0,0)))]
                        ]
                        window["-STATUS-"].update("PASS", text_color="green")
                    else:
                        output = [
                            [sg.Text("", text_color="green", font=["",20,"bold"], justification="center", size=(10, 1))],               
                            [sg.Text("FAIL", text_color="red", font=["",50,"bold"], justification="center", size=(10, 1))],
                            [sg.Text(str(rowData))],
                            [sg.OK(size=(10,1), font=["",50,""],p=((15,0),(0,0)))]
                        ]
                        window["-STATUS-"].update("FAIL", text_color="red")
                    pathStr = str(savePath + "/Reports/" + light_string + '_'+ serialNum + '_' + dateString)
                    print(pathStr)
                    saveReport(hidden, pathStr)
                    choice, _ = sg.Window('Measurment Data', output, modal=False).read(close=True)
            window['-MEASURE-'].update(disabled=False)
        elif event == "-LIGHT-":
            if values["-LIGHT-"] == 'JWL':
                window["-SIZE-"].update(values=other_size)
            else:
                window["-SIZE-"].update(values=linear_size)

        elif event == "-LIGHT_STRING-":
            light_string = values["-LIGHT_STRING-"]

            if 'SVL' in light_string:
                window["-LIGHT_STRING-"].update(value='')

        elif event == "-SERIAL_NUM-":
            serial_num = values["-SERIAL_NUM-"]

            if 'S' not in serial_num:
                window["-SERIAL_NUM-"].update(value='')       

    window.close()

with Vimba.get_instance() as vimba:
    cams = vimba.get_all_cameras()
    cams[0].set_access_mode(AccessMode.Full)
    with cams[0] as cam:
        #cam.load_settings("EOLTestSettings.xml", PersistType.NoLUT)
        main()
