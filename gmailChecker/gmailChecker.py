#!/usr/bin/env python
import RPi.GPIO as GPIO, feedparser, time
from os import system
import datetime
import sys

dateScriptStarted = time.localtime()

DEBUG = 1
USERNAME = ""     # just the part before the @ sign, add yours here
PASSWORD = ""

NEWMAIL_OFFSET = 0        # ONLY notify if unread greater than this.
#MAIL_CHECK_FREQ = 60      # check mail every 60 seconds
CRON_PERIOD = 3600        # seconds between cron job executions
POLL_FREQUENCY = 3      #Gmail server will be re-polled every POLL_FREQUENCY executions

def poll():
   global newmails
   newmails = int(feedparser.parse("https://" + USERNAME + ":" + PASSWORD +"@mail.google.com/gmail/feed/atom")["feed"]["fullcount"])

def main():
   if newmails > NEWMAIL_OFFSET:
      newMail()

def newMail():  #function to execute if new emails are found.
   color='FF0000'
   system("python /home/pi/SCRIPTS/rgbLED/rgbStrip.py -p 'FFFFFF {0} 1' ".format(color))

poll()
index=1
while 1:
   now = time.localtime()
   delta = datetime.datetime.fromtimestamp(time.mktime(now)) - datetime.datetime.fromtimestamp(time.mktime(dateScriptStarted))
   print delta.total_seconds()
   if delta.total_seconds() > (CRON_PERIOD - 20):
      break
   index += 1
   if index % POLL_FREQUENCY == 0:
      poll()
   main()
   time.sleep(newmails*2 + 10)

