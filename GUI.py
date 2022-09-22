
import PySimpleGUI as sg
import cv2

from matplotlib import use as use_agg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import AVT_BeamAnalysis_NOCAMERA as data
import JWL_NOCAM as JWL



def pack_figure(graph, figure):
    canvas = FigureCanvasTkAgg(figure, graph.Widget)
    plot_widget = canvas.get_tk_widget()
    plot_widget.pack(side='top', fill='both', expand=1)
    return plot_widget

def plot_figure(index, x, y):
    fig = plt.figure(index)         # Active an existing figure
    ax = plt.gca()                  # Get the current axes
    ax.cla()                        # Clear the current axes
    if index == 1:
        ax.set_title("Horizontal Profile")
    else:
        ax.set_title("Vertical Profile")
    plt.plot(x, y)                  # Plot y versus x as lines and/or markers
    fig.canvas.draw()  


fig1 = plt.figure(1)                # Create a new figure
ax1 = plt.subplot(111)              # Add a subplot to the current figure.
fig2 = plt.figure(2)                # Create a new figure
ax2 = plt.subplot(111)              # Add a subplot to the current figure.

use_agg('TkAgg')
sg.theme("DarkGrey2")

image_column = [
    [sg.Text("Beam Analysis", size=(60, 1), justification="center")],
    [sg.Image(filename="", key="-IMAGE-", size=(10, 10))],
    [sg.Button("Exit", size=(10, 1))],
    [sg.Button("JWL", size =(10, 1))],
    [sg.Button("LSR", size =(10, 1))],
]

graph_column = [
    [sg.Text("Graph Analysis", size=(60, 1), justification="center")],
    [sg.Graph((600, 400), (0, 0), (640, 480), key="Graph1")],
    [sg.Graph((600, 400), (0, 0), (640, 480), key="Graph2")],
]

# Define the window layout
layout = [
    [sg.Column(image_column),
    sg.VSeperator(),
    sg.Column(graph_column)],
]

# Create the window and show it without the plot
window = sg.Window('OpenCV Integration', layout, finalize=True)
frame = cv2.imread("test.PNG")
graph1 = window["Graph1"]
graph2 = window["Graph2"]
plt.ioff()
pack_figure(window["Graph1"], fig1)
pack_figure(graph2, fig2)
x = 0
y = 0
plot_figure(1, x, y)
plot_figure(2, x, y)


while True:   
    event, values = window.read(timeout=20)
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    elif event == "JWL":
        frame = JWL.image
        plot_figure(1, JWL.horiz_x, JWL.horiz_y)
        plot_figure(2, JWL.vert_x, JWL.vert_y)
    elif event == "LSR":
        frame = data.image
        plot_figure(1, data.horiz_x, data.horiz_y)
        plot_figure(2, data.vert_x, data.vert_y)


    imgbytes = cv2.imencode(".png", frame)[1].tobytes()
    window["-IMAGE-"].update(data=imgbytes)

window.close()

