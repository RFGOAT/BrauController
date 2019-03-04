import ClassesBraucon
import RPi.GPIO as GPIO
import time as tm
import numpy as np
import threading as trd
from scipy.ndimage.interpolation import shift
import os
import time 
from time import sleep
from datetime import datetime
import os

# SPI Setup
csPin   = 8
misoPin = 9
mosiPin = 10
clkPin  = 11
# Max31865 Initialization
max31865 = ClassesBraucon.max31865(csPin,misoPin,mosiPin,clkPin)
# Variables
rootdir = os.path.dirname(os.path.realpath(__file__))+'/'
filepath = rootdir + 'logfile.csv'
file = open(filepath, "a")

    
def Pt100_Filter_C():
    
    global TempValBuffer
    
    FilterBuffer = np.zeros(50, dtype=float)
    
    while True:
        for i in range (48):
            T = max31865.readTemp()
            FilterBuffer = shift(FilterBuffer,1,cval= T)
            tm.sleep(0.02)
        
        FilterBuffer = np.sort(FilterBuffer, axis=0)
        IQR_Mean = np.mean(FilterBuffer[12:36])

        print(str(IQR_Mean) + ' GrC')
        now = datetime.now()
        file.write(str(now)+","+str(IQR_Mean) + "\n")
        file.flush()
        

def Background():
    Pt100_Mean_C()

#Start Thread
TempThread = trd.Thread(target=Background)
TempThread.start()
