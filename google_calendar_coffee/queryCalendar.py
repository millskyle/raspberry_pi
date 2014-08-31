import gdata.calendar.service
import gdata.service
import atom.service
import gdata.calendar
import gdata.calendar
import atom
import getopt
import sys
import string
import subprocess
import time
import xe
from feed.date.rfc3339 import tf_from_timestamp
import datetime
from datetime import datetime as dt
from google_calendar_config import google_account, google_password

#import RPi.GPIO as GPIO
#We need to log in to the GoogleCalendar service programatically.
objCal = gdata.calendar.service.CalendarService() #Make a calendar service object
objCal.email = google_account #your email
objCal.password = google_password #your password
objCal.source = 'RaspberryPi_CoffeeScheduler' #Name it something to make Google happy.
objCal.ProgrammaticLogin() #Log in to Google Calendar


def main():
   #Clear the at queue, if the script is running, then we'll re-add anything that is needed.
   ppproces = subprocess.Popen(["/bin/bash","/home/pi/SCRIPTS/coffee/addToQueue.sh","","ClearQueue"])
   ppproces.wait()
   print "1. Cleared"

   #Perform the Google Calendar query
   text_query='Make coffee' #The event title must match this string
   query = gdata.calendar.service.CalendarEventQuery('default', 'private', 'full', text_query)
   query.start_min = time.strftime('%Y-%m-%dT%H:%M:%S-05:00',time.localtime())
   max = dt.now() + datetime.timedelta(minutes = 120)
   query.start_max = max.strftime('%Y-%m-%dT%H:%M:%S-05:00')
   print "Querying for events between {0} and {1}.".format(query.start_min,query.start_max)
   print "Current time: ",time.strftime('%Y-%m-%dT%H:%M:%S-05:00',time.localtime())
   feed = objCal.CalendarQuery(query)
   print "2. Queried"

   #Parse the results
   for i, an_event in enumerate(feed.entry):
      print an_event
      for a_when in an_event.when:
         eTime = time.localtime(tf_from_timestamp(a_when.start_time)) #event time
         cTime = time.localtime() # current time
         delta = datetime.datetime.fromtimestamp(time.mktime(eTime)) - datetime.datetime.fromtimestamp(time.mktime(cTime)) #start time/ current time difference

         if delta.total_seconds() < 0:
            print "Event is in the past"
            proces = subprocess.Popen(["/bin/bash","/home/pi/SCRIPTS/coffee/addToQueue.sh","","ClearQueue"])
            proces.wait()
         elif delta.total_seconds() > 0:
            print "Event is in the future.  We'll add it to the queue."
            #Queue the coffee making
            proces = subprocess.Popen(["/bin/bash","/home/pi/SCRIPTS/coffee/addToQueue.sh",time.strftime("%H:%M %B %d", eTime),"AddToQueue"])
            proces.wait()
      break
   print "4. Finished"


main()
