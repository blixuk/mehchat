#!/usr/bin/env python3

import socket
import threading
import sys
import datetime

class Server():
	# Using 'socket.AF_INET' = IPv4 and 'SOCK_STREAM' = TCP connection
	connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Defining socket as a TCP Socket
	connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	connections = []
	address = '0.0.0.0' # Default address
	port = 8080  # Default port
	running = True # Keep alive while true
	debugging = True
	timestamp = datetime.datetime.now()

	def __init__(self, address, port):
		if address != None:
			self.setAddress(address)
			self.debug('Init', 'Set Address', address)
		
		if port != None:
			self.setPort(port)
			self.debug('Init', 'Set Port', port)
		
		self.setConnection()

	def debug(self, function, information, arguments = ''):
		if self.debugging == True:
			print(f'{self.timestamp} : {function} : {information} - {arguments}')

	def setAddress(self, address):
		self.address = str(address) # Set the global address

	def setPort(self, port):
		self.port = int(port) # Set the global port

	def connectionHandler(self, connection, address):
		self.debug('Connection', 'New Connection', address)
		while True:
			try:
				data = connection.recv(1024) # Recinging data from connection
			except Exception as e:
				self.debug('Connection', 'Received Data', f'{e} : {address}')
				self.connections.remove(connection)
				self.debug('Connection', 'Closed Connection', address)
				connection.close()
				break # Breaking out if no data

			if not data:
				self.connections.remove(connection)
				self.debug('Connection', 'Closed Connection', address)
				connection.close()
				break # Breaking out if no data
			self.debug('Connection', 'Received Data', f'{data} : from :  {address}')

			for client in self.connections:
				if client != connection:
					client.send(data)
				self.debug('Connection', 'Sending Data', data)

	def setConnection(self):
		self.connection.bind((self.address, self.port)) # Binding our socket to an IP Address and port
		self.debug('Socket', 'Binding', f'{self.address}:{self.port}')
		self.connection.listen(1) # Listing on that port for connections
		self.debug('Socket', 'Listening')
	
	def run(self):
		self.debug('Main', 'Server Running')
		while self.running == True:
			connection, address = self.connection.accept() # Accepting connections and getting their Address
			
			connectionThread = threading.Thread(target=self.connectionHandler, args=(connection, address)) # Assigning our thread to the connection handler function
			connectionThread.daemon = True # Allowing exiting without closing threads
			connectionThread.start() # Running the thread

			self.connections.append(connection) # Adding the new connection to the connections list

class Client():
	# Using 'socket.AF_INET' = IPv4 and 'SOCK_STREAM' = TCP connection
	connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Defining socket as a TCP Socket
	connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	address = '0.0.0.0' # Default address
	port = 8080 # Default port
	running = True # Keep alive while true
	debugging = False
	timestamp = datetime.datetime.now()

	def __init__(self, address, port):
		if address != None:
			self.setAddress(address)
			self.debug('Init', 'Set Address', address)
		
		if port != None:
			self.setPort(port)
			self.debug('Init', 'Set Port', port)

		self.setConnection()

	def debug(self, function, information, arguments = ''):
		if self.debugging == True:
			print(f'{self.timestamp} : {function} : {information} - {arguments}')

	def setAddress(self, address):
		self.address = str(address) # Set the global address

	def setPort(self, port):
		self.port = int(port) # Set the global port

	def messageHandler(self):
		while True:
			message = input('')
			self.connection.send(bytes(message, 'utf-8'))
			self.debug('Message', 'Sent Message', message)

	def setConnection(self):
		self.connection.connect((self.address, self.port))
		self.debug('Connection', 'Connecting', f'{self.address}:{self.port}')

		messageThread = threading.Thread(target=self.messageHandler) # Assigning our thread to the connection handler function
		messageThread.daemon = True # Allowing exiting without closing threads
		messageThread.start() # Running the thread

	def run(self):
		self.debug('Main', 'Client Running')
		while self.running == True:
			message = self.connection.recv(1024) # Recinging data from connection
			self.debug('Main', 'Message Received', message)

			if not message:
				self.connection.close()
				self.debug('Main', 'Message Received', 'ERROR')
				break # Breaking out if no data

			print(str(message, 'utf-8'))

def main():
	if (len(sys.argv) > 1):
		Client(None, None).run() # Define the Client
	else:
		Server(None, None).run() # Define the Server

if __name__ == "__main__":
	main()
