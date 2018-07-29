import ClassesBraucon
import RPi.GPIO as GPIO
import time as tm
import numpy as np
import threading as trd
from scipy.ndimage.interpolation import shift

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
#RC-Pins & LED Setup
ON_CH  = 21
OFF_CH = 26
##LED    = 16
GPIO.setup(ON_CH,GPIO.OUT)
GPIO.setup(OFF_CH,GPIO.OUT)
##GPIO.setup(LED,GPIO.OUT)
GPIO.output(ON_CH,GPIO.LOW)
GPIO.output(OFF_CH,GPIO.LOW)
##GPIO.output(LED,GPIO.LOW)
# SPI Setup
csPin   = 8
misoPin = 9
mosiPin = 10
clkPin  = 11 
# Max31865 Initialization
max = ClassesBraucon.max31865(csPin,misoPin,mosiPin,clkPin)
# Variables
CurrSocketState = False # False--> Socket OFF
TempValBuffer = np.arange(10,dtype=float)
rootdir = '/home/pi/braucon/'

# Functions
def Socket (NewSocketState):
    
    global CurrSocketState
    
    if (CurrSocketState == False and NewSocketState == True):
        GPIO.output(ON_CH,GPIO.HIGH)
        tm.sleep(0.3)
        GPIO.output(ON_CH,GPIO.LOW)
        CurrSocketState = True
    elif (CurrSocketState == True and NewSocketState == False):
        GPIO.output(OFF_CH,GPIO.HIGH)
        tm.sleep(0.3)
        GPIO.output(OFF_CH,GPIO.LOW)
        CurrSocketState = False
        
    return CurrSocketState

    
def Pt100_Mean_C(n,delay,delay2):
    
    global TempValBuffer
    
    MeanBuffer = np.arange(n, dtype=float)
    
    while True:
        for i in range (n):
            T = max.readTemp()
            MeanBuffer = shift(MeanBuffer,1,cval= T)
            tm.sleep(delay)
        mean = np.round(np.mean(MeanBuffer),2)
        print(str(mean) + 'GrC')
        TempValBuffer = shift(TempValBuffer,1,cval=mean)
        ######print(str(TempValBuffer) + 'TempvalBuffer')
        tm.sleep(delay2) # New value every X seconds



    
def Fridge(Low,High):
    
    while True:
            
        meanT = TempValBuffer[0]
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
    Pt100_Mean_C(5,2,290) #alle 5 minuten

def Main():
    print('Start - Power ON')
    Socket(True)
    Fridge(12,15)


## Initialize Temperature measurement
TempThread = trd.Thread(target=Background) #new values with 2Hz
MainThread = trd.Thread(target=Main) 
##TempThread.daemon = True
TempThread.start()
tm.sleep(660) #TempValBuffer has to be filled
MainThread.start()






