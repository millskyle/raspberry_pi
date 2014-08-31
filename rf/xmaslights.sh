
if [ "$1" ==  "on" ]; then
   sudo python /home/pi/SCRIPTS/rf/outlet_control.py 'C1-1' > /dev/null 2>/dev/null 
   sudo python /home/pi/SCRIPTS/rf/outlet_control.py 'C2-1' > /dev/null 2>/dev/null
   sudo python /home/pi/SCRIPTS/rf/outlet_control.py 'A3-1' > /dev/null 2>/dev/null
else
   sudo python /home/pi/SCRIPTS/rf/outlet_control.py 'C1-0' > /dev/null 2>/dev/null
   sudo python /home/pi/SCRIPTS/rf/outlet_control.py 'C2-0' > /dev/null 2>/dev/null
   sudo python /home/pi/SCRIPTS/rf/outlet_control.py 'A3-0' > /dev/null 2>/dev/null
fi
