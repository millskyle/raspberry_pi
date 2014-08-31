#!/bin/sh

cd /home/pi/SCRIPTS/coffee/
echo `pwd`
python /home/pi/SCRIPTS/coffee/makeCoffee.py
echo "SCRIPT RAN.  RUN BY "
echo `logname`
echo "t"
