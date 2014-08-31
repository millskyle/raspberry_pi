import time
import os
import sys

brewTime=415 #how long does it take to make coffee?

def main():
   #Coffee On
   os.system("sudo python /home/pi/SCRIPTS/rf/outlet_control.py 'C3-1'")
   logFile = open("/home/pi/SCRIPTS/coffee/log.htm","a")
   logFile.write(time.strftime('%Y-%m-%d %H:%M:%S     Coffee maker turned on.\n',time.localtime()))
   logFile.close()
   time.sleep(brewTime)
   #Coffee Off
   os.system("sudo python /home/pi/SCRIPTS/rf/outlet_control.py  'C3-0'")
   logFile = open("/home/pi/SCRIPTS/coffee/log.htm","a")
   logFile.write(time.strftime('%Y-%m-%d %H:%M:%S     Coffee maker turned off.\n', time.localtime()))
   logFile.close()
   #Make sure it's really off
   os.system("sudo python /home/pi/SCRIPTS/rf/outlet_control.py 'C3-0'")

main()
