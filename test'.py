import math

from matplotlib import use as use_agg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import PySimpleGUI as sg

def pack_figure(graph, figure):
    canvas = FigureCanvasTkAgg(figure, graph.Widget)
    plot_widget = canvas.get_tk_widget()
    plot_widget.pack(side='top', fill='both', expand=1)
    return plot_widget

def plot_figure(index, theta):
    fig = plt.figure(index)         # Active an existing figure
    ax = plt.gca()                  # Get the current axes
    x = [degree for degree in range(1080)]
    y = [math.sin((degree+theta)/180*math.pi) for degree in range(1080)]
    ax.cla()                        # Clear the current axes
    ax.set_title(f"Sensor Data {index}")
    ax.set_xlabel("X axis")
    ax.set_ylabel("Y axis")
    ax.set_xscale('log')
    ax.grid()
    plt.plot(x, y)                  # Plot y versus x as lines and/or markers
    fig.canvas.draw()               # Rendor figure into canvas

# Use Tkinter Agg
use_agg('TkAgg')

layout = [[sg.Graph((640, 480), (0, 0), (640, 480), key='Graph1'), sg.Graph((640, 480), (0, 0), (640, 480), key='Graph2')]]
window = sg.Window('Matplotlib', layout, finalize=True)


# Initial
graph1 = window['Graph1']
graph2 = window['Graph2']
plt.ioff()                          # Turn the interactive mode off
fig1 = plt.figure(1)                # Create a new figure
ax1 = plt.subplot(111)              # Add a subplot to the current figure.
fig2 = plt.figure(2)                # Create a new figure
ax2 = plt.subplot(111)              # Add a subplot to the current figure.
pack_figure(graph1, fig1)           # Pack figure under graph
pack_figure(graph2, fig2)
theta1 = 0                          # theta for fig1
theta2 = 90                         # theta for fig2
plot_figure(1, theta1)
plot_figure(2, theta2)

while True:

    event, values = window.read(timeout=10)

    if event == sg.WINDOW_CLOSED:
        break
    elif event == sg.TIMEOUT_EVENT:
        theta1 = (theta1 + 40) % 360
        plot_figure(1, theta1)
        theta2 = (theta2 + 40) % 260
        plot_figure(2, theta2)

window.close()