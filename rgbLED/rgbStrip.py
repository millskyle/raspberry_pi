import math
import datetime
import os
from Adafruit_PWM_Servo_Driver import PWM
import colorsys
import time
import sys
import getopt
from pprint import pprint
lockfile='/home/pi/SCRIPTS/rgbLED/lockfile'
brightFreeze='/home/pi/SCRIPTS/rgbLED/brightnessFreeze'
wait=0
while os.path.isfile(lockfile):
   time.sleep(0.01)
   wait+=1
   if wait % 100 == 0:
      print "Found Lock File.  Waited for {0} seconds".format(wait * 0.01)
   if wait==40:
      #We've waited too long.  Lock file might be stuck.  Let's remove it.
      if os.path.isfile(lockfile):
         os.remove(lockfile)
      break

open(lockfile,'w').write("This is a lock file.  If it exists, the script will pause execution")
global lastcolour
global lastbrightness
global lastexplicitcolour
lastcolour="000000"
lastbrightness="1.0"
lastcolour=open("/home/pi/SCRIPTS/rgbLED/lastcolor",'r').read()
lastexplicitcolour=open("/home/pi/SCRIPTS/rgbLED/lastexplicitcolor",'r').read()
lastbrightness=open("/home/pi/SCRIPTS/rgbLED/lastexplicitbrightness",'r').read()
print "Last Brightness: " + lastbrightness
if lastbrightness=="":
   lastbrightness="0.05"
if len(lastcolour) <> 6:
   lastcolour="000000"
if len(lastexplicitcolour) <> 6:
   lastexplicitcolour="000000"
pwm = PWM(0x40, debug=False)
#pwm.setPWMFreq(1000)


def main():
   try:
      opts, args = getopt.getopt(sys.argv[1:], 'x:r:t:s:d:b:a:',["hex=","rgb=","transition=","brightness=","alterbrightness=","rgbClock","freezeBrightness","unfreezeBrightness","rainbow"])
   except getopt.GetoptError:
      argError()
      usage()
      sys.exit(2)
   for opt, arg in opts:
      if opt in ('-x', '--hex'):
         value=arg
         if len(value)==6:
            hexSet(value)
         else:
            usage()
         sys.exit(2)
      elif opt in ('-r', '--rgb'):
         value=arg.split()
         rgbSet(value)
         sys.exit(2)
      elif opt in ('-t', '--transition'):
         value=arg.split()
         transitionSet(value)
         sys.exit(2)
      elif opt in ('-s','--strobe'):
         value=arg.split()
         strobeSet(value)
      elif opt in ('-d','--doubletransition'):
         value=arg.split()
         doubleTransitionSet(value)
      elif opt in ('-b','--brightness'):
         value=arg
         snapToBrightness(value)
      elif opt in ('-a','--adjustbrightness'):
         value=arg
         adjustBrightnessSet(value)
      elif opt in ('--rgbClock'):
         rgbClock()
      elif opt in ('--freezeBrightness'):
         freezeBrightness(True)
      elif opt in ('--unfreezeBrightness'):
         freezeBrightness(False)
      elif opt in ('--rainbow'):
         rainbow()
      else:
         usage()
         sys.exit(2)
   if len(opts)==0:
      errorFlash()
   cleanup()

def rgbSet(data):
   vR=int(data[0])
   vG=int(data[1])
   vB=int(data[2])
   writeToController(vR,vG,vB)
   global lastexplicitcolour
   lastexplicitcolour=rgb2hex(vR,vG,vB)

def freezeBrightness(status=True):
   if os.path.isfile(brightFreeze):
      os.remove(brightFreeze)
   else:
      f = open(brightFreeze,"w")
      f.write("")
      f.close()

def hexSet(data):
   vR=hex2rgb(data)[0]
   vG=hex2rgb(data)[1]
   vB=hex2rgb(data)[2]
   writeToController(vR,vG,vB)
   global lastexplicitcolour
   lastexplicitcolour=rgb2hex(vR,vG,vB)

def transitionSet(data):
   smoothTransition(data[0],data[1],100,int(data[2]))
   global lastexplicitcolour
   lastexplicitcolour=data[1]

def doubleTransitionSet(data):
   returnTo=lastcolour
   smoothTransition(lastcolour,data[0],50,int(data[1]))
   time.sleep(0.2)
   smoothTransition(data[0],returnTo,50,int(data[1]))

def adjustBrightnessSet(data):
   global newBrightness
   if float(data) < float(lastbrightness):
      data=str(float(lastbrightness)-0.01)
   print "New desired Brightness: {0}".format(data)
   if round(float(lastbrightness),3)==round(float(data),3):
      print "Already at this brightness"
      return
   else:
      open("/home/pi/SCRIPTS/rgbLED/lastexplicitbrightness",'w').write(data)
   new=alterBrightness([hex2rgb(lastexplicitcolour)[0],hex2rgb(lastexplicitcolour)[1],hex2rgb(lastexplicitcolour)[2]],float(data))
   newHex=rgb2hex(new[0],new[1],new[2])
   if newHex<>"000000":
      smoothTransition(lastcolour,newHex,80,2,True)

def strobeSet(data):
   lstcolour=open("/home/pi/SCRIPTS/rgbLED/lastcolor",'r').read()
   c1=hex2rgb(data[0])
   c2=hex2rgb(data[1])
   for i in xrange(int(data[3])):
      writeToController(c1[0],c1[1],c1[2])
      time.sleep(1.0/int(data[2]))
      writeToController(c2[0],c2[1],c2[2])
      time.sleep(1.0/int(data[2]))
   writeToController(hex2rgb(lstcolour)[0],hex2rgb(lstcolour)[1],hex2rgb(lstcolour)[2])

def rgbClock():
   thisTime = time.localtime()
   print thisTime
   if thisTime[3]>=12:
      nowTime=(thisTime[3]-12)*60 + thisTime[4]
   else:
      nowTime=thisTime[3]*60 + thisTime[4]
   normalised_time=nowTime*2 / 1440.0  #Time normalised from 1 to 100
   color=colorsys.hsv_to_rgb(normalised_time,1.0,1.0)
   rgb = [int(i * 255) for i in color]
   writeToController(rgb[0],rgb[1],rgb[2])


def rainbow(repeat=5):
   for i in xrange(repeat):
      for n in xrange(1,100):
         color=colorsys.hsv_to_rgb(float(n)/100.0,1.0,1.0)
         rgb = [int(i * 255) for i in color]
         writeToController(rgb[0],rgb[1],rgb[2])
         time.sleep(0.03)




def alterBrightness(rgb,brightness):
   #Returns rgb list transformed to brightness.  Brightness is float between 0 and 1.
   def ensureNonZero(rgb, brightness):
      hsv=list(colorsys.rgb_to_hsv(rgb[0]/255.0,rgb[1]/255.0,rgb[2]/255.0))
      hsv[2]=float(brightness)
      if hsv[2] < 0.0:
         hsv[2]=0
         print "Brightness bottomed out"
      elif hsv[2] > 1.0:
         hsv[2]=1.0
         print "Brightness hit maximum of 1.0"
      return [int(i*255) for i in list(colorsys.hsv_to_rgb(hsv[0],hsv[1],hsv[2]))]

   returnValue="000000"
   if brightness<>0:
      while returnValue=="000000":
         brightness = float(brightness) + 0.001
         returnValue = ensureNonZero(rgb, brightness)

   return returnValue

def getBrightness(hexa):
   return float(list(colorsys.rgb_to_hsv(hex2rgb(hexa)[0]/255.0,hex2rgb(hexa)[1]/255.0,hex2rgb(hexa)[2]/255.0))[2])

def snapToBrightness(brightness):
   lastcolourlist=[hex2rgb(lastexplicitcolour)[0],hex2rgb(lastexplicitcolour)[1],hex2rgb(lastexplicitcolour)[2]]
   rgb2=alterBrightness(lastcolourlist,brightness)
   explicitWriteToController(rgb2[0],rgb2[1],rgb2[2])

def smoothTransition(hex1,hex2,steps=100,duration=5,exp=False):
   print "Executing smooth transition from {0} to {1}".format(hex1,hex2)
   steps=duration*10
   if hex1==hex2:
      print "Already at colour #{0}".format(hex1)
      return
   r1=cR=hex2rgb(hex1)[0]
   g1=cG=hex2rgb(hex1)[1]
   b1=cB=hex2rgb(hex1)[2]
   r2=hex2rgb(hex2)[0]
   g2=hex2rgb(hex2)[1]
   b2=hex2rgb(hex2)[2]

   sR=(abs(r1-r2)/float(steps))
   sG=(abs(g1-g2)/float(steps))
   sB=(abs(b1-b2)/float(steps))

   rSign=gSign=bSign=1

   if r2 < r1:
      rSign=-1
   if g2 < g1:
      gSign=-1
   if b2 < b1:
      bSign=-1

   timer=duration / float(steps)

   for i in xrange(steps):
      time.sleep(timer)
      cR=cR+sR*rSign
      cG=cG+sG*gSign
      cB=cB+sB*bSign
#      print "Current step is {0},{1},{2}:    Step {3}.".format(int(cR),int(cG),int(cB),i)
      if exp==True:
         explicitWriteToController(int(cR),int(cG),int(cB))
      else:
         writeToController(int(cR),int(cG),int(cB))

def rgb2pwm(rgb):
   return int(rgb*4094/float(255)) #colorlinearisation[int(rgb)]

def hex2rgb(hexa):
   r=hexa[0:2]
   g=hexa[2:4]
   b=hexa[4:6]
   rgb=[0,0,0]
   if r=="XX":
      rgb[0]=int(lastcolour[0:2],16)
   else:
      rgb[0]=int(r,16)

   if g=="XX":
      rgb[1]=int(lastcolour[2:4],16)
   else:
      rgb[1]=int(g,16)

   if b=="XX":
      rgb[2]=int(lastcolour[4:6],16)
   else:
      rgb[2]=int(b,16)

   return rgb

def rgb2hex(R,G,B):
   return "{0}{1}{2}".format(hex(R).split('x')[1].zfill(2),hex(G).split('x')[1].zfill(2),hex(B).split('x')[1].zfill(2))

def writeToController(xR,xG,xB):
   global lastcolour
   global lastexplicitcolour
   R,G,B=alterBrightness([xR,xG,xB], getBrightness(lastcolour))
   pwm.setPWM(4,0,rgb2pwm(R))
   pwm.setPWM(6,0,int(rgb2pwm(G)*0.8))
   pwm.setPWM(5,0,int(rgb2pwm(B)*0.70))
   lastcolour= rgb2hex(R,G,B) #"{0}{1}{2}".format(hex(R).split('x')[1].zfill(2),hex(G).split('x')[1].zfill(2),hex(B).split('x')[1].zfill(2))
   lastexplicitcolour = rgb2hex(xR,xG,xB)
# print "Writing {0}, {1}, {2}".format(rgb2pwm(R),rgb2pwm(G),rgb2pwm(B))
   #open("/home/pi/SCRIPTS/rgbLED/lastcolor",'w').write(lastcolour)


def explicitWriteToController(xR,xG,xB):
#Write a color to the controller without changing to the current brightness.
   global lastcolour
   pwm.setPWM(4,0,rgb2pwm(xR))
   pwm.setPWM(6,0,int(rgb2pwm(xG)*0.8))
   pwm.setPWM(5,0,int(rgb2pwm(xB)*0.70))
   lastcolour= rgb2hex(xR,xG,xB)


def cleanup():
   open("/home/pi/SCRIPTS/rgbLED/lastcolor",'w').write(lastcolour)
   open("/home/pi/SCRIPTS/rgbLED/lastexplicitcolor",'w').write(lastexplicitcolour)
   if os.path.isfile(lockfile):
      os.remove(lockfile)



import atexit
atexit.register(cleanup)

colorlinearisation={
0:0,
1:1,
2:5,
3:10,
4:30,
5:75,
6:120,
7:180,
8:260,
9:339,
10:342,
11:345,12:349,13:352,14:355,15:358,16:361,17:365,18:368,19:371,20:375,21:378,22:382,23:385,24:389,25:392,26:396,27:400,28:403,29:407,30:411,31:415,32:419,33:423,34:427,35:431,36:435,37:439,38:443,39:447,40:451,41:456,42:460,43:464,44:469,45:473,46:478,47:482,48:487,49:492,50:496,51:501,52:506,53:511,54:516,55:521,56:526,57:531,58:536,59:541,60:547,61:552,62:557,63:563,64:568,65:574,66:579,67:585,68:591,69:597,70:602,71:608,72:614,73:620,74:626,75:633,76:639,77:645,78:652,79:658,80:665,81:671,82:678,83:685,84:691,85:698,86:705,87:712,88:720,89:727,90:734,91:741,92:749,93:756,94:764,95:772,96:779,97:787,98:795,99:803,100:811,101:820,102:828,103:836,104:845,105:853,106:862,107:871,108:880,109:888,110:897,111:907,112:916,113:925,114:935,115:944,116:954,117:964,118:973,119:983,120:993,121:1004,122:1014,123:1024,124:1035,125:1046,126:1056,127:1067,128:1078,129:1089,130:1100,131:1112,132:1123,133:1135,134:1147,135:1158,136:1170,137:1183,138:1195,139:1207,140:1220,141:1232,142:1245,143:1258,144:1271,145:1284,146:1298,147:1311,148:1325,149:1339,150:1353,151:1367,152:1381,153:1395,154:1410,155:1425,156:1439,157:1455,158:1470,159:1485,160:1501,161:1516,162:1532,163:1548,164:1565,165:1581,166:1597,167:1614,168:1631,169:1648,170:1666,171:1683,172:1701,173:1719,174:1737,175:1755,176:1774,177:1792,178:1811,179:1830,180:1850,181:1869,182:1889,183:1909,184:1929,185:1949,186:1970,187:1991,188:2012,189:2033,190:2054,191:2076,192:2098,193:2120,194:2143,195:2166,196:2188,197:2212,198:2235,199:2259,200:2283,201:2307,202:2331,203:2356,204:2381,205:2407,206:2432,207:2458,208:2484,209:2511,210:2537,211:2564,212:2592,213:2619,214:2647,215:2675,216:2704,217:2733,218:2762,219:2791,220:2821,221:2851,222:2881,223:2912,224:2943,225:2975,226:3006,227:3038,228:3071,229:3104,230:3137,231:3170,232:3204,233:3239,234:3273,235:3308,236:3344,237:3379,238:3415,239:3452,240:3489,241:3526,242:3564,243:3602,244:3641,245:3680,246:3719,247:3759,248:3800,249:3840,250:3881,251:3923,252:3965,253:4008,254:4051,255:4094,}

def enforceRange(minn,maxx,value):
   if value<minn:
      return minn
   elif value > maxx:
      return maxx
   else:
      return value








def usage():
   print """
This program controls the PWM (Pulse Width Modulation) driver to control RGB LEDs.  There are multiple "modes":

   -x    Change LEDs instantaneously to a hexadecimal colour value.
            ie:   python rgbstrip.py C301FF

   -r    Change LEDs instantaneously to an RGB colour value. Values between 0 and 255.
            ie:   python rgbStrip.py '255 0 53'

   -t    Smoothly changes LEDs from one colour to another over a period of time.
         Only hexadecimal colour values are allowed. Transition speed is specified in
         seconds (approximately).
            ie:   python rgbStrip.py 'FF0000 0000FF 5'

   -d    Double transition.  This takes one hex number and an integer. The program changes
         the colour from the current colour, to the specified colour and back. Good for
         notifications or warnings.
            ie:   python rgbStrip.py '00FF00 3'

   -s    Stobe Mode.  String containing two hex colors an integer, indicating the number
         of strobes per second and integer representing number of flashes.
            ie:   python rgbStrip.py 'FF0000 FFFF00 6 30'

   -b    Brightness mode.  Changes current color to the same colour, but at a different
         brightness. Parameter must be floating point number between 0 and 1 (0 is off,
         1 is full brightness).  All future colour changes will respect this brightness
         until a further brightness command is executed.

   -a    Adjust brightness.  Smoothly adjusts the brightness.

   "XXXXXX"    This special "Hex string" can be used in place of the starting colour
               for a transition.  When done, the last known colour written to the
               driver will be used in place of XXXXXX.  This makes it simple to change
               smoothly to a new colour without remebering what you last wrote to the
               driver.

   Examples:

      rgbStrip.py -x EfDa54
      rgbStrip.py -r "255 255 100"
      rgbStrip.py -t "FF00FF 00FF00 6"
      rgbStrip.py -s "FF0000 FFFF00 10 100"

   Called without any arguments, the program will flash through the rainbow.

"""


def argError():
   print """
!!!ERROR!!! You did not provide a valid argument, or you didn't pass a parameter with an argument that requires a parameter.  See usage below:

"""



main()

