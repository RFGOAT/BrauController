import ClassesBraucon
import RPi.GPIO as GPIO
import time as tm
import numpy as np
import threading as trd
from scipy.ndimage.interpolation import shift


# SPI Setup
csPin   = 8
misoPin = 9
mosiPin = 10
clkPin  = 11
# Max31865 Initialization
max = ClassesBraucon.max31865(csPin,misoPin,mosiPin,clkPin)

    
def Pt100_Mean_C(n,delay,delay2):
    
    
    MeanBuffer = np.arange(n, dtype=float)
    
    while True:
        for i in range (n):
            T = max.readTemp()
            MeanBuffer = shift(MeanBuffer,1,cval= T)
            tm.sleep(delay)
        mean = np.round(np.mean(MeanBuffer),2)
        print(str(mean) + ' GrC')
        tm.sleep(delay2)

def Background():
    Pt100_Mean_C(5,1,1)

#Start Thread
TempThread = trd.Thread(target=Background)
TempThread.start()
