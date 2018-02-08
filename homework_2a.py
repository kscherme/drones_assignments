#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Katie Schermerhorn

from __future__ import print_function
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative

import argparse
parser = argparse.ArgumentParser(description='Commands vehicle using vehicle.homework_2a.')
parser.add_argument('--connect', help="Vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

connection_string = args.connect
sitl = None

# Start SITL if no connection string specified
if not connection_string:
	import dronekit_sitl
	sitl = dronekit_sitl.start_default()
	connection_string = sitl.connection_string()

# Connect to the Vehicle
vehicle = connect(connection_string, wait_ready=True)

# Do not try to arm until autopilot is read
while not vehicle.is_armable:
	print(" Waiting for vehicle to initialize...")
	time.sleep(1)

print("Arming motors")
# Copter should arm in GUIDED mode
vehicle.mode = VehicleMode("GUIDED")
vehicle.armed = True

# Confirm vehicle armed before attemption to take off
while not vehicle.armed:
	print(" Waiting for arming...")
	time.sleep(1)


print("Taking off!")
vehicle.simple_takeoff(30) # take off to target altitude

while True:
	print(" Altitude:", vehicle.location.global_relative_frame.alt)
	# Break and return from function just below target altitude
	if vehicle.location.global_relative_frame.alt >= 30 * 0.95:
		print("Reached target altitude")
		break
	time.sleep(1)


vehicle.airspeed = 10

point1 = LocationGlobalRelative(41.71435, -86.24325, 30)
vehicle.simple_goto(point1)

# sleep so we can see the change in map
time.sleep(20)

point2 = LocationGlobalRelative(41.71525,-86.24325, 30)
vehicle.simple_goto(point2, groundspeed=10)

time.sleep(20)

print("Returning to Launch")
vehicle.mode = VehicleMode("RTL")

vehicle.close()

if sitl:
	sitl.stop()















