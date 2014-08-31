#!/bin/bash
#WARNING:  This script clears the "at" queues `c` and `d`. Do not add any jobs to these queues or they will be removed.




#Remove all jobs in queue c
for j in `(atq -q c; atq -q d) | awk '{ print $1 }'`; do
	atrm "$j"
done


if [ "$2" == "ClearQueue" ]
then
	echo "All pending jobs cleared."
else
      time1=`date +%s -d "$1 - 15 minutes"` #fifteen minutes before event
      #Add the new job.
      time2=`date +%s` #current time
      checkTime=`date '+%H:%M %B %d' -d "+1 minute"`  #one minute in future
   #if the current time is within 15 minutes of the event, then query the calendar again in a minute to ensure we catch last-minute cancellations
   if [ $time1 -lt $time2 ]
      then 
         echo "python /home/pi/SCRIPTS/coffee/queryCalendar.py" | at -M -q d "$checkTime"
      fi
   echo "python /home/pi/SCRIPTS/coffee/makeCoffee.py" | at -M -q c "$1"  #queue the coffee making for the time passed as the first argument
fi
