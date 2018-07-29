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
max = ClassesBraucon.max31865(csPin,misoPin,mosiPin,clkPin)
# Variables
file = open("/home/pi/braucon/logfile.csv", "a")

    
def Pt100_Mean_C(n,delay,delay2):
    
    
    MeanBuffer = np.arange(n, dtype=float)
    
    while True:
        for i in range (n):
            T = max.readTemp()
            MeanBuffer = shift(MeanBuffer,1,cval= T)
            tm.sleep(delay)
        mean = np.round(np.mean(MeanBuffer),2)
        print(str(mean) + ' GrC')
        now = datetime.now()
        file.write(str(now)+","+str(mean) + "\n")
        file.flush()
        
        tm.sleep(delay2)

#        os.system('/etc/init.d/networking restart')


def Background():
    Pt100_Mean_C(5,1,600)

#Start Thread
TempThread = trd.Thread(target=Background)
TempThread.start()
