import RPi.GPIO as GPIO
import time as tm 
import math
import numpy as np 
from scipy.ndimage.interpolation import shift

csPin = 8
misoPin = 9
mosiPin = 10
clkPin = 11

' These are SUBFUNCTIONS for use inside this file only'

def setupGPIO():
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(csPin, GPIO.OUT)
	GPIO.setup(misoPin, GPIO.IN)
	GPIO.setup(mosiPin, GPIO.OUT)
	GPIO.setup(clkPin, GPIO.OUT)

	GPIO.output(csPin, GPIO.HIGH)
	GPIO.output(clkPin, GPIO.LOW)
	GPIO.output(mosiPin, GPIO.LOW)


def sendByte(byte):
	for bit in range(8):
		GPIO.output(clkPin, GPIO.HIGH)
		if (byte & 0x80):
			GPIO.output(mosiPin, GPIO.HIGH)
		else:
			GPIO.output(mosiPin, GPIO.LOW)
		byte <<= 1
		GPIO.output(clkPin, GPIO.LOW)

def recvByte():
	byte = 0x00
	for bit in range(8):
		GPIO.output(clkPin, GPIO.HIGH)
		byte <<= 1
		if GPIO.input(misoPin):
			byte |= 0x1
		GPIO.output(clkPin, GPIO.LOW)
	return byte	



def writeRegister(regNum, dataByte):
	GPIO.output(csPin, GPIO.LOW)
	
	# 0x8x to specify 'write register value'
	addressByte = 0x80 | regNum;
	
	# first byte is address byte
	sendByte(addressByte)
	# the rest are data bytes
	sendByte(dataByte)

	GPIO.output(csPin, GPIO.HIGH)

def readRegisters(regNumStart, numRegisters):
	out = []
	GPIO.output(csPin, GPIO.LOW)
	# 0x to specify 'read register value'
	sendByte(regNumStart)
	
	for byte in range(numRegisters):	
		data = recvByte()
		out.append(data)

	GPIO.output(csPin, GPIO.HIGH)
	return out



def calcPT100Temp(RTD_ADC_Code):
	R_REF = 430.0 # Reference Resistor
	Res0 = 100.0; # Resistance at 0 degC for 400ohm R_Ref
	a = .00390830
	b = -.000000577500
	# c = -4.18301e-12 # for -200 <= T <= 0 (degC)
	#c = -0.00000000000418301
	# c = 0 # for 0 <= T <= 850 (degC)
	#print ("RTD ADC Code: %d" % RTD_ADC_Code)
	Res_RTD = (RTD_ADC_Code * R_REF) / 32768.0 # PT100 Resistance
	#print ("PT100 Resistance: %f ohms" % Res_RTD)
	temp_C = -(a*Res0) + math.sqrt(a*a*Res0*Res0 - 4*(b*Res0)*(Res0 - Res_RTD))
	temp_C = temp_C / (2*(b*Res0))
    
	if (temp_C < 0): #use straight line approximation if less than 0
		# Can also use python lib numpy to solve cubic
		# Should never get here in this application
		temp_C = (RTD_ADC_Code/32) - 256
	return temp_C



' These are MAINFUNCTIONS for use inside this file only'


def readTemp():
	# b10000000 = 0x80
	# 0x8x to specify 'write register value'
	# 0xx0 to specify 'configuration register'
	#
	# 0b10110010 = 0xB2
	# Config Register
	# ---------------
	# bit 7: Vbias -> 1 (ON)
	# bit 6: Conversion Mode -> 0 (MANUAL)
	# bit5: 1-shot ->1 (ON)
	# bit4: 3-wire select -> 1 (3 wire config)
	# bits 3-2: fault detection cycle -> 0 (none)
	# bit 1: fault status clear -> 1 (clear any fault)
	# bit 0: 50/60 Hz filter select -> 0 (60Hz)
	#
	# 0b11010010 or 0xD2 for continuous auto conversion 
	# at 60Hz (faster conversion)
	#one shot
	writeRegister(0, 0xB2)
	# conversion time is less than 100ms
	tm.sleep(.1) #give it 100ms for conversion
	# read all registers
	out = readRegisters(0,8)


	[rtd_msb, rtd_lsb] = [out[1], out[2]]
	rtd_ADC_Code = (( rtd_msb << 8 ) | rtd_lsb ) >> 1
		
	temp_C = calcPT100Temp(rtd_ADC_Code)
#
#		[hft_msb, hft_lsb] = [out[3], out[4]]
#		hft = (( hft_msb << 8 ) | hft_lsb ) >> 1
#		#print ("high fault threshold: %d" % hft)
#
#		[lft_msb, lft_lsb] = [out[5], out[6]]
#		lft = (( lft_msb << 8 ) | lft_lsb ) >> 1
#		#print ("low fault threshold: %d" % lft)

	status = out[7]
		#
		# 10 Mohm resistor is on breakout board to help
		# detect cable faults
		# bit 7: RTD High Threshold / cable fault open 
		# bit 6: RTD Low Threshold / cable fault short
		# bit 5: REFIN- > 0.85 x VBias -> must be requested
		# bit 4: REFIN- < 0.85 x VBias (FORCE- open) -> must be requested
		# bit 3: RTDIN- < 0.85 x VBias (FORCE- open) -> must be requested
		# bit 2: Overvoltage / undervoltage fault
		# bits 1,0 don't care	
		#print "Status byte: %x" % status

	if ((status & 0x80) == 1):
		print("High threshold limit (Cable fault/open)")
	if ((status & 0x40) == 1):
		print("Low threshold limit (Cable fault/short)")
	if ((status & 0x04) == 1):
		print("Overvoltage or Undervoltage Error")
		    
	return temp_C
		

		
def Pt100_Filter_C(gain,offset):
    
    global TempValBuffer
    
    FilterBuffer = np.zeros(50, dtype=float)
    
    while True:
        for i in range (48):
            T = readTemp()
            FilterBuffer = shift(FilterBuffer,1,cval= T)
            tm.sleep(0.02)
        
        FilterBuffer = np.sort(FilterBuffer, axis=0)
        IQR_Mean = np.mean(FilterBuffer[12:36])
        IQR_MeanCal = np.round(gain * IQR_Mean + offset,2) ##calibrated
        TempValBuffer = shift(TempValBuffer,1,cval=IQR_MeanCal)
        

 

	

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
