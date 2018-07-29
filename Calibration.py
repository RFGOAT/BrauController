import ClassesBraucon
import RPi.GPIO as GPIO
import time as tm
import numpy as np
from scipy.ndimage.interpolation import shift

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# SPI Setup
csPin   = 8
misoPin = 9
mosiPin = 10
clkPin  = 11
# Max31865 Initialization
max31865 = ClassesBraucon.max31865(csPin,misoPin,mosiPin,clkPin)
# Variables

rootdir = '/home/pi/braucon/'

   
    
def Pt100_Filter_Celsius(n,delay,f_type):
    
    TempBuffer = np.arange(n, dtype=float)
    for i in range (n):
        T = max31865.readTemp()
        TempBuffer = shift(TempBuffer,1,cval= T)
        tm.sleep(delay)
        
        if(f_type == 'mean'):
            val = np.round(np.mean(TempBuffer),2)
        elif(f_type == 'median'):
            val = np.round(np.median(TempBuffer),2)
        else:
            print('no filter_type defined')

    return val


def Calibration():
    
    print('Place sensor in Cold-water')
    print('Start Calibration with Enter')
    Tp_1 = float(input('Enter Temperature'))
    Te_1 = Pt100_Filter_Celsius(20,0.1,'median')
    
    print('Place sensor in Hot-water')
    #print('Start Calibration with Enter')
    Tp_2 = float(input('Enter Temperature'))
    Te_2 = Pt100_Filter_Celsius(20,0.1,'median')
    
    CalVal = np.arange(2,dtype=float)
    CalVal[0] = (Tp_2-Tp_1)/(Te_2-Te_1) # Gain
    CalVal[1] = (Tp_1*Te_2 - Tp_2*Te_1) / (Te_2-Te_1)   # Offset
    
    print('Gain ' + str(CalVal[0]))
    print('Offset ' + str(CalVal[1]))
    
    return CalVal


np.savetxt(rootdir + 'Calibration.data', Calibration())













