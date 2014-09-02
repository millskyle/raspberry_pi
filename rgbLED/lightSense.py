#!/usr/bin/python
import math,os
from random import randrange
from Adafruit_I2C import * ## Code from Github
import time
address = 0x29 ## Device address
control_on = 0x03 ## "On" value
control_off = 0x00 ## "Off" value

samples=1

i2c = Adafruit_I2C(address)
setanyway=0

def setB(b):
   global brightness
   brightness=b
   if os.path.isfile("/home/pi/SCRIPTS/rgbLED/lastexplicitbrightness"):
      lb = float(open("/home/pi/SCRIPTS/rgbLED/lastexplicitbrightness",'r').read())
      if b <= 0.05:
         setanyway=1
      else:
         setanyway=0
      if ((b <=  (lb - 0.05)) or (b >= (lb + 0.05))  or setanyway) and not os.path.isfile("/home/pi/SCRIPTS/rgbLED/brightnessFreeze"):
         os.system("python /home/pi/SCRIPTS/rgbLED/rgbStrip.py -a {0}  ".format(brightness))
         print "Changing brightness"
      else:
         print "Brightness too close to last brightness"

def enable():
   i2c.write8(0x80, control_on) ##Writes on value to control register
   time.sleep(0.5)
   i2c.write8(0x81, 0x12)

def disable():
   i2c.write8(0x80, control_off) ##Writes off value to control register

def getLight():
   Channel0 = i2c.readU16(0xAC) ## Read total light (from channel 0)
   Channel1 = i2c.readU8(0xAE) ## Read infrared light (from channel 1)
   return Channel0, Channel1

disable()
last=[0]*5

sTime = time.time()
print "Started at {0}".format(sTime)
sMinute=time.localtime()[4]

while time.localtime()[4]==sMinute:
   data = 0
   while data==0:
      read = getLight()
      data = read[0]
      if data==0:
         enable()

   sumc0=sumc1=0
   for i in xrange(samples):
      thisRead = getLight()
   #   print thisRead
      sumc0 = sumc0 + thisRead[0]
      sumc1 = sumc1 + thisRead[1]
      #time.sleep(0.4)

   c0 = sumc0*10 / samples
   c1 = sumc1*10 / samples

   frac = float(c1)/float(c0)
   #print "frac={0}".format(frac)


   if 0 < frac <= 0.50:
      lux = 0.0304 * c0 - 0.062 * c0 * ( pow(c1/c0,1.4))
   elif 0.50 < frac <=0.61:
      lux = 0.0224*c0  -  0.031*c1
   elif 0.61 < frac <=0.80:
      lux = 0.0128*c0  -  0.0153*c1
   elif 0.80 < frac <= 1.30:
      lux = 0.00146*c0 - 0.001128*c1
   else:
      lux = 0

   lux = int(lux)

   s = c0# - c1

   print "Read: {0}".format(s)
   if s <=500.0:
      t= 0.00000038*float(s+20.0)**2
      print "polynomial"
   else:
      t = (0.207102) * math.log(float(s)) - 0.98406 - 0.2
      print "logarithmic"

#   if last[4]<=last[3] and t > last[4]:
#      t = t - 0.05

#   if last[3] <= t <= last[4]:
#      t = last[3]

   print t

   if t > 0.9:
      t=1.0
   elif t < 0.005:
      t=0.005
   print t
   last.pop(0)
   last.append(t)
   print last
   setB(t)
   time.sleep(0.5)



