import time
import RPi.GPIO as GPIO
pinToUse=22
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)



#GPIO.setup(pinToUse, GPIO.OUT)
GPIO.setup(pinToUse, GPIO.IN)

while True:
   print GPIO.input(pinToUse)
   time.sleep(0.2)

