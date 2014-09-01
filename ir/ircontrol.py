from time import sleep
import RPi.GPIO as GPIO
from string import split
import datetime
import time
import sys
import os

lockfile='/tmp/ir_lock'
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
pinToUse=17
#Send the code `repeat` times (for redundancy)
repeat=5 # times to send code (for redundancy)

starting = "00000000000000011111111"

#dictionary defining codes for the rf outlets
codes = {
'on':"0101010101010101011101110111011101110111011101110111011101110101010101010101011101110111011101110",
'off':"0101010101010101011101110111011101110111011101110101110111010101010101110101011101110111011101110",
}



low_len = 110./192000.
hi_len = 92./192000. 

ending = "1111111111111111111"

def send_code(name):
   snooze = 0.00060 #each bit is held for this long
   print "Sending code called {0}.".format(name)
   code=codes[name]
   print "Code is {0}.".format(code)
#   GPIO.cleanup()
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(pinToUse, GPIO.OUT)
   for i in xrange(repeat):
      for bit in starting + code + ending:
         if bit=="0":
            GPIO.output(pinToUse,True)
            time.sleep(hi_len)
         elif bit=="1":
            GPIO.output(pinToUse,False)
            time.sleep(low_len)
      time.sleep(1)
   GPIO.setup(pinToUse, GPIO.IN)
   GPIO.cleanup

send_code(sys.argv[1])

#GPIO.setup(pinToUse, GPIO.IN)
#GPIO.cleanup
if os.path.isfile(lockfile):
   os.remove(lockfile)
time.sleep(0.2)


