#!/bin/bash

export TERM=xterm
cd "/home/pi/SCRIPTS/coffee/"
date > last_cron_execution
python queryCalendar.py
