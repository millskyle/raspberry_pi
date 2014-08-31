from time import sleep
import RPi.GPIO as GPIO
from string import split
import datetime
import time
import sys
import os

lockfile='/tmp/rf_outlet_lock'
wait=0
while os.path.isfile(lockfile):
   time.sleep(0.01)
   wait+=1
   print "Found Lock File.  Waited for {0} seconds".format(wait/10.0)
   if wait==750:
      #We've waited too long.  Lock file might be stuck.  Let's remove it.
      if os.path.isfile(lockfile):
         os.remove(lockfile)
      break

open(lockfile,'w').write("This is a lock file.  If it exists, the script will pause execution")

#Use GPIO pin 4
pinToUse=4
#Send the code `repeat` times (for redundancy)
repeat=20 # times to send code (for redundancy)

#dictionary defining codes for the rf outlets
codes = {
'A1-1':"1000111011101000111010001000100011101000100010001110100010001000000000000",
'A1-0':"1000111011101000111010001000100010001110100010001110100010001000000000000",
'A2-1':"1000111011101000111010001000100010001000111010001110100010001000000000000",
'A2-0':"1000111011101000111010001000100010001000100011101110100010001000000000000",
'A3-1':"1000111011101000111010001000111010001000100010001110100010001000000000000",
'A3-0':"1000111011101000111010001110100010001000100010001110100010001000000000000",
'C1-1':"1000111011101000111010001000100011101000100010001000100011101000000000000",
'C1-0':"1000111011101000111010001000100010001110100010001000100011101000000000000",
'C2-1':"1000111011101000111010001000100010001000111010001000100011101000000000000",
'C2-0':"1000111011101000111010001000100010001000100011101000100011101000000000000",
'C3-1':"1000111011101000111010001000111010001000100010001000100011101000000000000",
'C3-0':"1000111011101000111010001110100010001000100010001000100011101000000000000"
}


def send_code(name):
   snooze = 0.000489 #each bit is held for this long
   print "Sending code called {0}.".format(name)
   code=codes[name]
   print "Code is {0}.".format(code)
#   GPIO.cleanup()
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(pinToUse, GPIO.OUT)
   for i in xrange(repeat):
      for bit in code:
         if bit=="1":
            GPIO.output(pinToUse,True)
         elif bit=="0":
            GPIO.output(pinToUse,False)
         time.sleep(snooze)
      time.sleep(snooze*3)
   GPIO.setup(pinToUse, GPIO.IN)
   GPIO.cleanup

send_code(sys.argv[1])

#GPIO.setup(pinToUse, GPIO.IN)
#GPIO.cleanup
if os.path.isfile(lockfile):
   os.remove(lockfile)
time.sleep(0.2)


