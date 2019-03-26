import pt100_functions as Pt100

import RPi.GPIO as GPIO
import time as tm
import numpy as np
import threading as trd
import os
from scipy.ndimage.interpolation import shift

rootdir = os.path.dirname(os.path.realpath(__file__))+'/'


# Variables
TempValBuffer = np.zeros(10,dtype=float)


def Background():
    global TempValBuffer
    
    while True:
        TempValBuffer = Pt100.Pt100_Filter_C(gain,offset,TempValBuffer)
        print(TempValBuffer[0]) #last updated value

'START'
#Initialize Pt100 measurement
Pt100.setupGPIO()
gain,offset = np.loadtxt(rootdir + 'Calibration.data', dtype=float)

#Start Thread
TempThread = trd.Thread(target=Background)
TempThread.start()

