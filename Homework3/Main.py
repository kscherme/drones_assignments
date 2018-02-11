import os
import threading
from Connection import Connection
import socket
import socketutils
import time
import json
import dronekit
import dronekit_sitl

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

class Copter:
	def __init__(self, handshake_msg_queue, state_msg_queue):
		self.vehicle = None
		self.vid = None
		self.handshake_to_dronology_msgs = handshake_msg_queue
		self.state_to_dronology_msgs = state_msg_queue

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


		self.handshake_to_dronology_msgs.put_message(handshake_message.from_vehicle(self.vechicle, self.vid))
		print "sent handshake"

class DroneHandshakeMessage():

	def __init__(self, m_type='handshake', vid, data):
		self.m_type = m_type
		self.vid = vid
		self.data = data

	def from_vehicle(self, vehicle, vid, p2sac='../cfg/sac.json'):
		lla = vehicle.location.global_relative_frame
		data = {
			'yyy': "more params..."
			"xxx": "abc"
			'home': {'x': lla.lat,
		             'y': lla.lon,
		             'z': lla.alt},
		    		}

		message = {
				"type": self.m_type,
				"uavid": self.vid,
				"sendtimestamp": time.time(),
				data
			}
		return message





if __name__ == '__main__':
	# instance of Runner class
	runner = Runner()
	# start GCS
	print "Starting runner"
	runner.start()

