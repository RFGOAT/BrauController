import pt100_functions as Pt100

import RPi.GPIO as GPIO
from datetime import datetime
import time as tm
import numpy as np
import threading as trd
import os
from scipy.ndimage.interpolation import shift


rootdir = os.path.dirname(os.path.realpath(__file__))+'/'
filepath = rootdir + 'logfile.csv'
file = open(filepath, "a")


def Background():
    TempValBuffer = np.zeros(10,dtype=float)
    
    while True:
        TempValBuffer = Pt100.Pt100_Filter_C(gain,offset,TempValBuffer)
        print(TempValBuffer[0]) #last updated value
        
        now = datetime.now()
        file.write(str(now)+","+str(TempValBuffer[0]) + "\n")
        file.flush()
        
'START'
#Initialize Pt100 measurement
Pt100.setupGPIO()
gain,offset = np.loadtxt(rootdir + 'Calibration.data', dtype=float)
#Start Thread
TempThread = trd.Thread(target=Background)
TempThread.start()
