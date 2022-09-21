import sys
import os
from tkinter import *

window=Tk()

window.title("Smart Vision Lights Beam Analysis")
window.geometry('550x200')

def runJWL():
    os.system('python JWL_Measure.py')
def runRZL():
    os.system('python RZL_Measure.py')
def runLive():
    os.system('python liveView.py')
    
btn = Button(window, text="Capture JWL", bg="black", fg="white",command=runJWL)
btn.grid(column=1, row=1)
btn = Button(window, text="Capture RZL", bg="black", fg="white",command=runRZL)
btn.grid(column=2, row=1)
btn = Button(window, text=" Live ", bg="black", fg="white",command=runLive)
btn.grid(column=3, row=1)

window.mainloop()