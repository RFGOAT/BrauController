import RPi.GPIO as GPIO
import time as tm

ON_CH  = 21
OFF_CH = 26

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(ON_CH,GPIO.OUT)
GPIO.setup(OFF_CH,GPIO.OUT)

GPIO.output(ON_CH,GPIO.LOW)
GPIO.output(OFF_CH,GPIO.LOW)


'Variables'
CurrSocketState = False # False--> Socket OFF

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
        
   #return CurrSocketState

def ApplyDuty(ratio,T):
    Socket(True)
    tm.sleep(ratio*T)
    Socket(False)
    tm.sleep((1-ratio)*T)























