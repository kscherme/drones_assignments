#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Write a program so that your drone starts close to the center of the flying field,
takes off to an altitude of 30 meters, and then files a triangle by visiting two
adjacent corners, before returning to launch.
'''

from __future__ import print_function
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative


# Set up option parsing to get connection string
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
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True)

def arm_and_takeoff(aTargetAltitude):

	print("Basic pre-arm checks")
	# Do not try to arm until autopilot is read
	while not vehicle.is_armable:
		print(" Waiting for vehicle to initialize...")
		time.sleep(1)

	# Confirm vehicle armed before attemption to take off
	while not vehicle.armed:
		print(" Waiting for arming...")
		time.sleep(1)


	print("Taking off!")
	vehicle.simple_takeoff(aTargetAltitude) # take off to target altitude

	while True:
		print(" Altitude:", vehicle.location.global_relative_frame.alt)
		# Break and return from function just below target altitude
		if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
			print("Reached target altitude")
			break
		time.sleep(1)

def arm_and_takeoff(30)

print("Set default/target airspeed to 10")
vehicle.airspeed = 10

print("Going towards first point for 60 seconds ...")
point1 = LocationGlobalRelative(41.71435, -86.24325, 30)
vehicle.simple_goto(point1)

# sleep so we can see the change in map
time.sleep(60)

print("Going towards second point for 60 seconds (groundspeed set to 10 m/s) ...")
point2 = LocationGlobalRelative(41.71525,-86.24325, 30)
vehicle.simple_goto(point2, groundspeed=10)

# sleep so we can see the change in map
time.sleep(60)

print("Returning to Launch")
vehicle.mode = VehicleMode("RTL")

# Close vehicle object before exiting script
print("Close vehicle object")
vehicle.close()

# Shut down simulator if it was started.
if sitl:
	sitl.stop()















