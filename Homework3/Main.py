import os
import threading
from Connection import Connection
import socket
import socketutils

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
    			msgs.append(self.msgs.pop(0))
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

	def start(self):
		# Establish connection to dronology
		self.conn = Connection(self.from_dronology)

		# Establish connection to the drones
		self.control_station = ControlStation(self.conn, self.from_dronology, self.handshake_to_dronology, self.state_to_dronology)

		self.conn.start()
		self.control_station.start()


class ControlStation:
	def __init__(self, connection, from_dronology_msg_queue, handshake_to_dronology_msg_queue, state_to_dronology_msg_queue):
		self.conn = connection
		self.from_dronology_msgs = from_dronology_msg_queue
		self.handshake_to_dronology_msgs = handshake_to_dronology_msg_queue
		self.state_to_dronology_msgs = state_to_dronology_msg_queue

		self.from_d_worker = threading.Thread(target=self.from_d_work)
		self.to_d_worker = threading.Thread(target=self.to_d_work)

	def start(self):
		self.from_d_worker.start()
		self.to_d_worker.start()

	def from_d_work(self):
		cont = True
		while cont:
			in_msgs = self.from_dronology_msgs.get_messages()
			for msg in in_msgs:
				print msg

	def to_d_work(self):
		cont = True
		while cont:
			in_msgs = self.state_to_dronology_msgs.get_messages()
			for msg in in_msgs:
				print msg



runner = Runner()
runner.start()
# mq = MessageQueue()
# conn = Connection(mq) 
