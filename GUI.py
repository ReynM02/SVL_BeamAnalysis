
from email.errors import InvalidMultipartContentTransferEncodingDefect
from msilib.schema import Error
import PySimpleGUI as sg
import cv2
from matplotlib import use as use_agg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import measureLight as SLA # Smart Light Analyzer

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


fig1 = plt.figure(1)                # Create a new figure
ax1 = plt.subplot(111)              # Add a subplot to the current figure
fig2 = plt.figure(2)                # Create a new figure
ax2 = plt.subplot(111)              # Add a subplot to the current figure
hidden = True


use_agg('TkAgg')
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
    [sg.Combo(lights, default_value='LSR', key="-LIGHT-", enable_events=True)],
    [sg.Combo(linear_size, default_value='300', key="-SIZE-", enable_events=True)],
    [sg.Combo(colors, default_value='WHI', key="-COLORS-")]
]

image_column = [
    [sg.Text("\nBeam Analysis", size=(160, 5), justification="center", font=100)],
    [sg.Image(filename="", key="-IMAGE-", size=(100, 100), expand_x=True)],
    [sg.Column(lists)],
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
        light = values["-LIGHT-"]
        lightSize = values["-SIZE-"]
        color = values["-COLORS-"]
        try:
            frame, horiz_x, horiz_y, vert_x, vert_y = SLA.measure(light, lightSize, color)
            invalConfig = False
        except:
            invalConfig = True

        if invalConfig == True:
            sg.popup('Error: Invalid Light Configuration, Verify Selected Configuration.', title="Error: InvalLightConfig", modal=True)
        else:    
            plot_figure(1, horiz_x, horiz_y)
            plot_figure(2, vert_x, vert_y)
    if event == "-LIGHT-":
        if values["-LIGHT-"] == 'JWL':
            window["-SIZE-"].update(values=other_size)
        else:
            window["-SIZE-"].update(values=linear_size)


    imgbytes = cv2.imencode(".png", frame)[1].tobytes()
    window["-IMAGE-"].update(data=imgbytes)

window.close()

