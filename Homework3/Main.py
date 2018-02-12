import os
import threading
from Connection import Connection
import socket
import socketutils
import time
import json
import dronekit
import dronekit_sitl
from threading import Timer

class MessageQueue:
    def __init__(self):
    	self.lock = threading.Lock()
        self.msgs = []

    def put_message(self,msg):
    	with self.lock:
        	self.msgs.append(msg)

    def get_messages(self):
    	messages = []
    	with self.lock:
    		while self.msgs:
    			messages.append(self.msgs.pop(0))
    	return messages

class Runner:
	def __init__(self):
		# Connection with Dronology
		self.conn = None
		# Control Station
		self.control_station = None
		# Messages from Dronology
		self.from_dronology = MessageQueue()
		# Handshake messages to Dronology
		self.handshake_to_dronology = MessageQueue()
		# State messages to Dronology
		self.state_to_dronology = MessageQueue()
		# Messages from vehicle
		self.from_vehicle = MessageQueue()
		self.global_cfg = None
		self.drone_cfg = None

		# Load global config path
		try: 
			with open("../../git/DronologyCourse/python/edu.nd.dronology.gstation1.python/cfg/global_cfg.json",'r') as f:
				self.global_cfg = json.load(f)
		except Exception as e:
			print(e)

		# Load drone config
		try:
			with open("../../git/DronologyCourse/python/edu.nd.dronology.gstation1.python/cfg/drone_cfgs/nd.json",'r') as f:
				self.drone_cfg = json.load(f)
		except Exception as e:
			print(e)


	def start(self):
		# Establish connection to dronology
		self.conn = Connection(self.from_dronology)
		print "Established connection to dronology"

		# Establish control station
		self.control_station = ControlStation(self.conn, self.from_dronology, self.handshake_to_dronology, self.state_to_dronology, self.from_vehicle)
		print "Estalbished control station" 

		# Start receiving messages
		self.conn.start()
		# Start Control Station
		self.control_station.start()
		time.sleep(1)

		# Register drone
		self.drone_cfg['ardupath'] = self.global_cfg['ardupath']
		print self.drone_cfg
		self.from_vehicle.put_message(self.drone_cfg)


class ControlStation:
	def __init__(self, connection, from_dronology_msg_queue, handshake_to_dronology_msg_queue, state_to_dronology_msg_queue, new_vehicle_queue):
		self.conn = connection
		self.from_v_msgs = new_vehicle_queue
		self.from_dronology_msgs = from_dronology_msg_queue
		self.handshake_to_dronology_msgs = handshake_to_dronology_msg_queue
		self.state_to_dronology_msgs = state_to_dronology_msg_queue

		self.drone = None

		self.from_v_worker = threading.Thread(target=self.from_v_work)
		self.from_d_worker = threading.Thread(target=self.from_d_work)
		self.to_d_worker = threading.Thread(target=self.to_d_work)

	def start(self):
		self.from_v_worker.start()
		self.from_d_worker.start()
		self.to_d_worker.start()

	def from_v_work(self):
		cont = True
		while cont:
			v_messages = self.from_v_msgs.get_messages()

			for msg in v_messages:
				print "registering vehicle"
				self.register_vehicle(msg)

	def from_d_work(self):
		cont = True
		while cont:
			in_msgs = self.from_dronology_msgs.get_messages()
			for msg in in_msgs:
				print "from dronology:"
				print msg
				threading.Thread(target=self.handle_message, args=(msg,)).start()

	def to_d_work(self):
		cont = True
		while cont:
			messages = self.state_to_dronology_msgs.get_messages()
			for msg in messages:
				print "to dronology:"
				print msg
				success = self.conn.send(str(msg))
				if not success:
					self.state_to_dronology_msgs.put_message(msg)

			messages = self.handshake_to_dronology_msgs.get_messages()
			for msg in messages:
				print "to dronology:"
				print msg
				success = self.conn.send(str(msg))
				if not success:
					self.handshake_to_dronology_msgs.put_message(msg)

			time.sleep(.1)

	def register_vehicle(self, v_spec):
		vehicle = Copter(self.handshake_to_dronology_msgs, self.state_to_dronology_msgs)

		print "Vehicle initialized"

		vehicle.connect_vehicle(**v_spec)
		self.drone = vehicle

	def handle_message(self, msg):
		if isinstance(self.drone, Copter):
			self.drone.handle_command(msg)



class Copter:
	def __init__(self, handshake_msg_queue, state_msg_queue):
		self.vehicle = None
		self.vid = None
		self.handshake_to_dronology_msgs = handshake_msg_queue
		self.state_to_dronology_msgs = state_msg_queue
		self.state_msg_timer = None
		self.state_interval = 1


	def connect_vehicle(self, vehicle_type, vehicle_id, home, ardupath):

		wait_till_armable = True
		defaults = os.path.join(ardupath, 'Tools', 'autotest', 'default_params', 'copter.parm')

		if len(home) == 2:
			home = tuple(home) + (0,0)
		else:
			home = tuple(home)

		if vehicle_type == 'VRTL':

			sitl_args = ['--home', ','.join(map(str, home))]
			print "Trying to launch SIT instance"
			sitl = dronekit_sitl.SITL(path=os.path.join(ardupath, 'build', 'sitl', 'bin', 'arducopter'))
			sitl.launch(sitl_args, await_ready=True)
			tcp, ip, port = sitl.connection_string().split(':')
			conn_string = ':'.join([tcp, ip, port])
			vehicle = dronekit.connect(conn_string)
			vehicle.wait_ready(timeout=120)
			print "Vehicle connected"

		if wait_till_armable:
			while not vehicle.is_armable:
				time.sleep(3)

		print "Vehicle armable"
		time.sleep(3)

		self.vehicle = vehicle
		self.vid = vehicle_id

		print self.vehicle

		handshake_message = DroneHandshakeMessage(self.vid, self.vehicle)


		self.handshake_to_dronology_msgs.put_message(handshake_message.from_vehicle(self.vehicle, self.vid))
		print "sent handshake"
		self.state_msg_timer = RepeatedTimer(self.state_interval, self.send_state_message)

	def send_state_message(self):
		message = self.gen_state_message()
		self.state_to_dronology_msgs.put_message(message)

	def gen_state_message(self):
		state_message = StateMessage(self.vid, self.vehicle)

		return state_message.from_vehicle(self.vehicle, self.vid)

	def handle_command(self, cmd):
		command = cmd["command"]

		commands = {
			1: "gotoLocation",
			2: "setArmed",
			3: "setGroundspeed",
			4: "setHome",
			5: "setMode",
			6: "takeoff"
		}

		if commands.get(command) == 1:
			self.goto(cmd)
		elif commands.get(command) == 2:
			self.set_armed(cmd)
		elif commands.get(command) == 3:
			self.set_groundspeed(cmd)
		elif commands.get(command) == 4:
			self.set_home(cmd)
		elif commands.get(command) == 5:
			self.set_mode(cmd)
		elif commands.get(command) == 6:
			self.takeoff(cmd)


	def set_mode(self, cmd):
		mode = cmd["data"]["mode"]
		self.vehicle.mode = dronekit.VehicleMode(mode)
		curr_mode = self.vehicle.mode.name

		while curr_mode != mode:
			self.vehicle.mode = dronekit.VehicleMode(mode)
			curr_mode = self.vehicle.mode.name

	def goto(self,cmd):
		self.vehicle.simple_goto(dronekit.LocationGlobalRelative(cmd["data"]["x"], cmd["data"]["y"], cmd["data"]["z"]))

	def set_armed(self, cmd):
		armed = cmd["data"]["armed"]
		if self.vehicle.armed != armed:
			if armed:
				while not self.vehicle.is_armable:
					time.sleep(2)

			self.vehicle.armed = armed
			while self.vehicle.armed !=armed:
				self.vehicle.armed = armed

	def set_groundspeed(self,cmd):
		speed = cmd["data"]["speed"]

	def set_home(self,cmd):
		self.vehicle.simple_goto(dronekit.LocationGlobalRelative(cmd["data"]["x"], cmd["data"]["y"], cmd["data"]["z"]))

	def takeoff(self,cmd):
		alt = cmd["data"]["altitude"]

		self.vehicle.mode = "GUIDED"
		armed = True
		if self.vehicle.armed != armed:
			if armed:
				while not self.vehicle.is_armable:
					time.sleep(2)

			self.vehicle.armed = armed
			while self.vehicle.armed !=armed:
				self.vehicle.armed = armed
		self.vehicle.simple_takeoff(alt)
	


class DroneHandshakeMessage():

	def __init__(self, vid, data, m_type='handshake'):
		self.m_type = m_type
		self.vid = vid
		self.data = data

	def from_vehicle(self, vehicle, vid):
		lla = vehicle.location.global_relative_frame

		message = {
				"type": self.m_type,
				"uavid": str(self.vid),
				"sendtimestamp": round(time.time()*1000),
				"data": {
					'yyy': "more params...",
					"xxx": "abc",
					'home': {'x': lla.lat,
		             			'y': lla.lon,
		             			'z': lla.alt},
		    				}}
		return message

class StateMessage():

	def __init__(self, vid, data, m_type='state'):
		self.m_type = m_type
		self.vid = vid
		self.data = data

	def from_vehicle(self, vehicle, vid):
		lla = vehicle.location.global_relative_frame
		att = vehicle.attitude
        	vel = vehicle.velocity


		battery = {
			'current': vehicle.battery.current,
            		'voltage': vehicle.battery.voltage,
            		'level': vehicle.battery.level,
        		}

		message = {
				"type": self.m_type,
				"uavid": str(self.vid),
				"sendtimestamp": round(time.time()*1000),
				"data": {
		            'location': {'x': lla.lat, 'y': lla.lon, 'z': lla.alt},
		            'attitude': {'x': att.roll, 'y': att.pitch, 'z': att.yaw},
		            'velocity': {'x': vel[0], 'y': vel[1], 'z': vel[2]},
		            'status': vehicle.system_status.state,
		            'mode': vehicle.mode.name,
		            'armed': vehicle.armed,
		            'armable': vehicle.is_armable,
		            'groundspeed': vehicle.airspeed,
		            'batterystatus': battery
				}}
		return message

class RepeatedTimer(object):
    def __init__(self, interval, func, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = func
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def set_interval(self, interval):
        self._timer.cancel()
        self.interval = interval
        self.start()

    def stop(self):
        self._timer.cancel()
        self.is_running = False





if __name__ == '__main__':
	# instance of Runner class
	runner = Runner()
	# start GCS
	print "Starting runner"
	runner.start()

