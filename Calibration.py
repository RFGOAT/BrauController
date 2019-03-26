import pt100_functions as Pt100

import RPi.GPIO as GPIO
import time as tm
import numpy as np
import os
from scipy.ndimage.interpolation import shift

# Variables
rootdir = os.path.dirname(os.path.realpath(__file__))+'/'


def Calibration():
    TempValBuffer = np.zeros(10,dtype=float)
    
    print('Place sensor in Cold-water')
    print('Start Calibration with Enter')
    Tp_1 = float(input('Enter Temperature'))
    TempValBuffer = Pt100.Pt100_Filter_C(gain,offset,TempValBuffer)
    Te_1 = TempValBuffer[0]
    
    print('Place sensor in Hot-water')
    Tp_2 = float(input('Enter Temperature'))
    TempValBuffer = Pt100.Pt100_Filter_C(gain,offset,TempValBuffer)
    Te_2 = TempValBuffer[0]

    
    CalVal = np.arange(2,dtype=float)
    CalVal[0] = (Tp_2-Tp_1)/(Te_2-Te_1) # Gain
    CalVal[1] = (Tp_1*Te_2 - Tp_2*Te_1) / (Te_2-Te_1)   # Offset
    
    print('Gain ' + str(CalVal[0]))
    print('Offset ' + str(CalVal[1]))
    
    return CalVal


'START'
#Initialize Pt100 measurement
Pt100.setupGPIO()
gain,offset = np.loadtxt(rootdir + 'Calibration.data', dtype=float)

np.savetxt(rootdir + 'Calibration.data', Calibration())













