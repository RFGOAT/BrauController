import ClassesBraucon
import RPi.GPIO as GPIO
import time as tm
import numpy as np
import threading as trd
from scipy.ndimage.interpolation import shift
#import matplotlib.pyplot as plt
import os

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
#RC-Pins & LED Setup
ON_CH  = 21
OFF_CH = 26
LED    = 2
GPIO.setup(ON_CH,GPIO.OUT)
GPIO.setup(OFF_CH,GPIO.OUT)
GPIO.setup(LED,GPIO.OUT)
GPIO.output(ON_CH,GPIO.LOW)
GPIO.output(OFF_CH,GPIO.LOW)
GPIO.output(LED,GPIO.LOW)
# SPI Setup
csPin   = 8
misoPin = 9
mosiPin = 10
clkPin  = 11
# Max31865 Initialization
max31865 = ClassesBraucon.max31865(csPin,misoPin,mosiPin,clkPin)
# Variables
CurrSocketState = False # False--> Socket OFF
TempValBuffer = np.arange(10,dtype=float)
#CycCounter = 0
rootdir = os.path.dirname(os.path.realpath(__file__))+'/'#'/home/pi/braucon/'

# Functions
def Socket (NewSocketState):#, CurrSocketState):
    
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

def ApplyDuty(ratio,T):
    Socket(True)
    tm.sleep(ratio*T)
    Socket(False)
    tm.sleep((1-ratio)*T)
        
def ReadPhasesCal():
    data = np.loadtxt(rootdir + 'MaischPhasen.dat', delimiter='\t',dtype='str')
    data = [x[2:-1] for x in data]
    phases = np.array([x.split(',') for x in data])
    gain,offset = np.loadtxt(rootdir + 'Calibration.data', dtype=float)        
    del data
   
    return phases,gain,offset
    
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
        IQR_MeanCal = np.round(gain * IQR_Mean + offset,2) ##calibrated
        TempValBuffer = shift(TempValBuffer,1,cval=IQR_MeanCal)
        

 
def CalcDeltaT (PhaseNum):
    
    global CycCounter
    
    T_soll = float(phases[PhaseNum][1])
    T_curr = TempValBuffer[0] #--- T_curr = Pt100_Mean_C(2,0.5)
    DeltaT = T_curr-T_soll
    print('T='+str(T_curr) +'GrC\t' +'Delta= ' + str(DeltaT) + 'GrC')

    return DeltaT

def HeatToTemp(PhaseNum):
    
    while ( CalcDeltaT(PhaseNum) < -0.4):
        
        Delta = abs(CalcDeltaT(PhaseNum))
        print(str(TempValBuffer[0]) + 'GrC')
        if (Delta > 5):
            Socket(True)
            tm.sleep(5)
        elif(Delta < 5 and Delta > 2.5): 
            print('75%')
            ApplyDuty(0.75,50)
##            tm.sleep(5)
        elif(Delta < 2.5  and Delta > 1.0):
            print('50%')
            ApplyDuty(0.5,40)
##            tm.sleep(10)
        elif(Delta < 1.0  and Delta > 0.3):
            print('15%')
            ApplyDuty(0.15,30)
            tm.sleep(20)
        else:
            print('0%')
            Socket(False)
            tm.sleep(5)
    print('Heating done!')

def Rast(PhaseNum):
    RastTime = int(phases[PhaseNum][2])
    
    for i in range(RastTime):
        print(phases[PhaseNum][2])
        print(str(RastTime-i) + ' minutes remaining')
        tm.sleep(40)
        if ( CalcDeltaT(PhaseNum) < -0.2):   
            Delta = abs(CalcDeltaT(PhaseNum))
            print(str(TempValBuffer[0]) + 'GrC')

            if(Delta < 2  and Delta > 0.8):
                print('15%')
                ApplyDuty(0.15,20)
            elif(Delta < 0.8  and Delta > 0.1):
                print('5%')
                ApplyDuty(0.05,20)
        else:
            print('0%')
            Socket(False)
            tm.sleep(20)
    
def ExecPhase(PhaseNum):
    print('Executing:  ' + phases[PhaseNum][0])
    T_soll = float(phases[PhaseNum][1])
    print('T_soll:  ' + str(T_soll) )#+ '°C')
    
    HeatToTemp(PhaseNum)
    print('Rast started:')    
    Rast(PhaseNum)
  
def Background():
    Pt100_Filter_C()

def Main():
    
   # fig = plt.figure()
    
    
    for i in range(1,len(phases)):
        print('starting phase ' + str(i))
        ExecPhase(i)
        
    GPIO.cleanup() 


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
tm.sleep(2) #TempValBuffer has to be filled
MainThread.start()






