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
    
def CalcDeltaT (PhaseNum):
        
    T_soll = float(phases[PhaseNum][1])
    
    'Delta T of last 3 values for safe rast transistions'
    T_curr = np.mean(TempValBuffer[0:3])
    #T_curr = TempValBuffer[0]
    
    DeltaT = T_curr-T_soll
    print('T='+str(T_curr) +'GrC\t' +'Delta= ' + str(DeltaT) + 'GrC')

    return DeltaT

def HeatToTemp(PhaseNum):
    
    while ( CalcDeltaT(PhaseNum) < -0.4):
        
        Delta = abs(CalcDeltaT(PhaseNum))
        print(str(TempValBuffer[0]) + 'GrC')
        if (Delta > 5):
            Sock.Socket(True)
            tm.sleep(5)
        elif(Delta < 5 and Delta > 2.5): 
            print('75%')
            Sock.ApplyDuty(0.75,50)
##            tm.sleep(5)
        elif(Delta < 2.5  and Delta > 1.0):
            print('50%')
            Sock.ApplyDuty(0.5,40)
##            tm.sleep(10)
        elif(Delta < 1.0  and Delta > 0.3):
            print('15%')
            Sock.ApplyDuty(0.15,30)
            tm.sleep(20)
        else:
            print('0%')
            Sock.Socket(False)
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
                Sock.ApplyDuty(0.15,20)
            elif(Delta < 0.8  and Delta > 0.1):
                print('5%')
                Sock.ApplyDuty(0.05,20)
        else:
            print('0%')
            Sock.Socket(False)
            tm.sleep(20)
    
def ExecPhase(PhaseNum):
    print('Executing:  ' + phases[PhaseNum][0])
    T_soll = float(phases[PhaseNum][1])
    print('T_soll:  ' + str(T_soll) )#+ '°C')
    
    HeatToTemp(PhaseNum)
    print('Rast started:')    
    Rast(PhaseNum)
  
def Background():
    global TempValBuffer
    
    while True:
        TempValBuffer = Pt100.Pt100_Filter_C(gain,offset,TempValBuffer)
        #print(TempValBuffer[0]) #last updated value

def Main():
    
    for i in range(1,len(phases)):
        print('starting phase ' + str(i))
        ExecPhase(i)
        
    GPIO.cleanup() 



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






