
import PySimpleGUI as sg
import cv2
import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import measureLight as SLA # Smart Light Analyzer
import datetime
import psutil
import os
from csv import writer

buffer = 0
user_list = psutil.users()
user = user_list[0].name
print(user)
savePath = 'C:/Users/' + user + '/Documents/SmartLightAnalyzer'
SLA.connect() # Connect to the electronics measurment tool

# Pack the Graphs from MatPlotLib to TKinter
def pack_figure(graph, figure):
    canvas = FigureCanvasTkAgg(figure, graph.Widget)
    plot_widget = canvas.get_tk_widget()
    plot_widget.pack(side='top', fill='both', expand=1)
    return plot_widget

# Cleats and Plots the Graphs
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
hidden = True



sg.theme("DarkGrey2")

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
    [sg.Text("\nBeam Analysis", size=(160, 5), justification="center", font=100)],
    [sg.Image(filename="", key="-IMAGE-", size=(100, 100), expand_x=True)],
    [sg.Text("Light P/N:"), sg.InputText(enable_events=True, size=(20, 5), key="-LIGHT_STRING-", do_not_clear=True)],
    [sg.Text("Light S/N:"), sg.InputText(enable_events=True, size=(20, 5), key="-SERIAL_NUM-", do_not_clear=True)],
    #[sg.Column(lists)],
    [sg.Button("Measure", size=(10,1), key="-MEASURE-")]
]

graph_column = [
    [sg.Text("Graph Analysis", size=(60, 1), justification="center")],
    [sg.Graph((200, 100), (0, 0), (200, 100), key="Graph1", expand_x=True, expand_y=True)],
    [sg.Graph((200, 100), (0, 0), (200, 100), key="Graph2", expand_x=True, expand_y=True)]
]

# Define the window layout
layout = [
    [sg.Column(image_column, expand_x=True, expand_y=True, size_subsample_width=2),
    sg.Button("Advanced", size=(10,1), key="-HIDE-"),
    sg.VSeperator(),
    sg.Column(graph_column, visible=False, key="-GRAPHS-", expand_x=True, expand_y=True)]
]

# Create the window and show it
window = sg.Window('Smart Vision Lights Beam Analysis', layout, finalize=True, resizable=True)
frame = cv2.imread("SVL_Stack.png")
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
imgbytes = cv2.imencode(".png", frame)[1].tobytes()
window["-IMAGE-"].update(data=imgbytes)
date = datetime.datetime.now()
month, day, year = date.month, date.day, date.year

print(month, day, year)

### --- Main Loop --- ###
while True:   
    event, values = window.read(timeout=20) # Reads window actions waiting for inputs
    # event is an action... event == "Exit" is Exit Button being pressed
    if event == "Exit" or event == sg.WIN_CLOSED: # Exit Button Pressed or Window Closed
        break
    elif event == "-HIDE-":
        if hidden == True:
            window['-GRAPHS-'].update(visible=True)
            hidden = False
        else:
            window['-GRAPHS-'].update(visible=False)
            hidden = True
    elif event == "-MEASURE-":
        window['-MEASURE-'].update(disabled=True)
        sysTime = datetime.datetime.now()
        dateString = sysTime.strftime("%Y-%m-%d") + '_' + sysTime.strftime("%H%M%S")
        light_string = values["-LIGHT_STRING-"]
        serialNum = values["-SERIAL_NUM-"]
        splitString = light_string.split('-')
        #print(splitString)
        mode = splitString[1]
        if mode != "MD" | "DO":
            try:
                light = splitString[0]
                mode = splitString[1]
                color = splitString[2]
            except IndexError:
                sg.popup('Error: Invalid Configuration, Enter Light P/N and S/N.', title="Error: InvalConfgErr", modal=True)
                print("lightgistics")
        else:
            try:
                light = splitString[0]
                color = splitString[1]
            except IndexError:
                sg.popup('Error: Invalid Configuration, Enter Light P/N and S/N.', title="Error: InvalConfgErr", modal=True)
                print("nonlightgistics")
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
            frame, horiz, vert, passFail = SLA.measure(light_string)
            invalConfig = False
        except:
            invalConfig = True

        if invalConfig == True:
            sg.popup('Error: Configuration Error, Verify Selected Configuration.', title="Error: LightConfigErr", modal=True)
        else:    
            plot_figure(1, horiz[0], horiz[1])
            plot_figure(2, vert[0], vert[1])
        #frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        if not os.path.exists(savePath):
            os.makedirs(savePath)
            os.makedirs(savePath+'/Images')
            os.makedirs(savePath+'/Data')
        imgPath = savePath+"/Images/"
        print (os.path.join(imgPath, light_string+'_'+serialNum+'_'+dateString+'.jpg'))
        isWritten = cv2.imwrite(imgPath+light_string+'_'+serialNum+'_'+dateString+'.jpg', frame)

        if isWritten:
            print("image saved")
        else:
            print("image not saved")

        imgbytes = cv2.imencode(".png", frame)[1].tobytes()
        window["-IMAGE-"].update(data=imgbytes)
        csvPath = savePath + '/Data/' + str(month) + '-' + str(day) + '-' + str(year) + '_Light_Measurements.csv'
        rowData = [light_string, serial_num]
        try:
            rowData.extend(passFail)
        except NameError:
            passFail = [0,0,0,0]
            rowData.extend(passFail)
        append_list_as_row(csvPath, rowData)
        sg.popup(str(rowData), title='Measurment Data', modal=False)
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

