#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Katie Schermerhorn

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

	print("Arming motors")
	# Copter should arm in GUIDED mode
	vehicle.mode = VehicleMode("GUIDED")
	vehicle.armed = True

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

arm_and_takeoff(15)

print("Set default/target airspeed to 10")
vehicle.airspeed = 10

print("Going towards point for 20 seconds ...")
point1 = LocationGlobalRelative(41.71435,-86.24307, 15)
vehicle.simple_goto(point1)

# sleep so we can see the change in map
# time.sleep(20)
for i in xrange(20,0,-1):
	time.sleep(1)
	print(vehicle.location.global_frame)


print("Going towards point for 10 seconds ...")
point1 = LocationGlobalRelative(41.71480,-86.24307, 15)
vehicle.simple_goto(point1)

# sleep so we can see the change in map
time.sleep(10)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point2 = LocationGlobalRelative(41.71484,-86.24306, 15)
vehicle.simple_goto(point2, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards third point for 5 seconds (groundspeed set to 10 m/s) ...")
point3 = LocationGlobalRelative(41.71485,-86.24305, 15)
vehicle.simple_goto(point3, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point4 = LocationGlobalRelative(41.71486,-86.24304, 15)
vehicle.simple_goto(point4, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point5 = LocationGlobalRelative(41.71487,-86.24300, 15)
vehicle.simple_goto(point5, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point6 = LocationGlobalRelative(41.71486,-86.24297, 15)
vehicle.simple_goto(point6, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point7 = LocationGlobalRelative(41.71485,-86.24295, 15)
vehicle.simple_goto(point7, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point8 = LocationGlobalRelative(41.71484,-86.24294, 15)
vehicle.simple_goto(point8, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71480,-86.24293, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71480,-86.24257, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(10)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71476,-86.24256, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71475,-86.24255, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71474,-86.24254, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71473,-86.24250, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71474,-86.24247, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71475,-86.24245, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71476,-86.24244, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71480,-86.24243, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71480,-86.24207, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(10)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71484,-86.24206, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71485,-86.24205, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71486,-86.24204, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71487,-86.24200, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71486,-86.24197, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71485,-86.24195, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71484,-86.24194, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71480,-86.24193, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71480,-86.24157, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(10)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71476,-86.24156, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71475,-86.24155, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71474,-86.24154, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71473,-86.24150, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71474,-86.24147, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71475,-86.24145, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71476,-86.24144, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71480,-86.24143, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71480,-86.24107, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(10)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71484,-86.24106, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71485,-86.24105, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71486,-86.24104, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71487,-86.24100, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71486,-86.24097, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71485,-86.24095, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71484,-86.24094, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards second point for 5 seconds (groundspeed set to 10 m/s) ...")
point9 = LocationGlobalRelative(41.71480,-86.24093, 15)
vehicle.simple_goto(point9, groundspeed=10)

# sleep so we can see the change in map
time.sleep(3)

print("Going towards first point for 5 seconds ...")
point1 = LocationGlobalRelative(41.71435,-86.24093, 15)
vehicle.simple_goto(point1)

# sleep so we can see the change in map
time.sleep(10)



print("Returning to Launch")
vehicle.mode = VehicleMode("RTL")

# Close vehicle object before exiting script
print("Close vehicle object")
vehicle.close()

# Shut down simulator if it was started.
if sitl:
	sitl.stop()