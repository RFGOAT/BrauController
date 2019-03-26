import pt100_functions as Pt100
import socket_functions as Sock

import RPi.GPIO as GPIO
import time as tm
import numpy as np
import threading as trd
import os

# LED Setup
LED  = 2
GPIO.setup(LED,GPIO.OUT)
GPIO.output(LED,GPIO.LOW)

# Variables
TempValBuffer = np.zeros(10,dtype=float)
rootdir = os.path.dirname(os.path.realpath(__file__))+'/'


def ReadPhasesCal():
    data = np.loadtxt(rootdir + 'MaischPhasen.dat', delimiter='\t',dtype='str')
    data = [x[2:-1] for x in data]
    phases = np.array([x.split(',') for x in data])
    gain,offset = np.loadtxt(rootdir + 'Calibration.data', dtype=float)        
    del data
   
    return phases,gain,offset


def Fridge(Low,High):
    
    while True:
            
        meanT = np.mean(TempValBuffer[0:3])
        print('meanT' + str(meanT)) 
            
        if ( meanT < Low):
            print('OFF')
            Socket(False)
            
        elif( meanT > High):
            Socket(True)
            print('ON')
        else:
            #Socket(False)
            print('else')
        tm.sleep(1800)
   
   
def Background():
    global TempValBuffer
    
    while True:
        TempValBuffer = Pt100.Pt100_Filter_C(gain,offset,TempValBuffer)
        #print(TempValBuffer[0]) #last updated value

def Main():
    print('Start - Power ON')
    Socket(True)
    Fridge(12,15)



'START'
#Initialize Pt100 measurement
Pt100.setupGPIO()
##Read Calibration and phases
#global phases,gain,offset
phases,gain,offset = ReadPhasesCal()
print(phases)
print('Gain: ' + str(gain) + ' Offset: ' + str(offset))

## Initialize Temperature measurement
TempThread = trd.Thread(target=Background) #new values with 2Hz
MainThread = trd.Thread(target=Main) 
##TempThread.daemon = True
TempThread.start()
tm.sleep(10) #TempValBuffer has to be filled
MainThread.start()




