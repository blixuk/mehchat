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
	seed = ''

	def __init__(self, address, port, seed):
		if address != None:
			self.setAddress(address)
			self.debug('Init', 'Set Address', address)
		
		if port != None:
			self.setPort(port)
			self.debug('Init', 'Set Port', port)

		if seed != None:
			self.setSeed(seed)
		
		self.debug('Init', 'Seed', self.getSeed())

		self.setConnection()

	def debug(self, function, information, arguments = ''):
		if self.debugging == True:
			print(f'{self.timestamp} : {function} : {information} - {arguments}')

	def setAddress(self, address):
		self.address = str(address) # Set the global address

	def setPort(self, port):
		self.port = int(port) # Set the global port

	def setSeed(self, seed):
		self.seed = Rose(seed).getSeed()

	def getSeed(self):
		return self.seed

	def setConnection(self):
		self.connection.bind((self.address, self.port)) # Binding our socket to an IP Address and port
		self.debug('Connection', 'Binding', f'{self.address}:{self.port}')
		self.connection.listen(1) # Listing on that port for connections
		self.debug('Connection', 'Listening')

	def connectionHandler(self, connection, address):
		if self.sendHandshake(connection, address) == True: # If Handshake is complete, Join server
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
	
	def sendHandshake(self, connection, address):
		connection.send(b'\x00' + bytes(str(self.getSeed()), 'utf-8'))
		self.debug('Connection', 'Sending Handshake', address)
		data = connection.recv(1024)

		if not data:
			sys.exit()

		if data[0:1] == b'\x01':
			print(str(data[1:], 'utf-8'))
			if str(data[1:], 'utf-8') == str(self.getSeed()):
				self.debug('Connection', 'Received Handshake', address)
				self.connections.append(connection) # Adding the new connection to the connections list
		else:
			sys.exit()

		return True

	def run(self):
		self.debug('Main', 'Server Running')
		while self.running == True:
			connection, address = self.connection.accept() # Accepting connections and getting their Address
			
			connectionThread = threading.Thread(target=self.connectionHandler, args=(connection, address)) # Assigning our thread to the connection handler function
			connectionThread.daemon = True # Allowing exiting without closing threads
			connectionThread.start() # Running the thread

			#self.connections.append(connection) # Adding the new connection to the connections list

class Client():
	# Using 'socket.AF_INET' = IPv4 and 'SOCK_STREAM' = TCP connection
	connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Defining socket as a TCP Socket
	connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	address = '0.0.0.0' # Default address
	port = 8080 # Default port
	running = True # Keep alive while true
	debugging = False
	timestamp = datetime.datetime.now()
	seed = ''

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

	def getSeed(self):
		return self.seed

	def setSeed(self, seed):
		self.seed = seed

	def messageHandler(self):
		while True:
			message = input('')
			message = bytes(Rose(self.getSeed()).encrypt(message), 'utf-8')

			if len(message) > 1024:
				for byte in range(0, len(message), 1024):
					self.connection.send(message[byte:byte+1024])
					self.debug('Message', 'Sent Chunk', message[byte:byte+1024])
			else:
				self.connection.send(message)
				self.debug('Message', 'Sent Message', message)

	def setConnection(self):
		self.connection.connect((self.address, self.port))
		self.debug('Connection', 'Connecting', f'{self.address}:{self.port}')

		if self.getHandshake() == True:
			messageThread = threading.Thread(target=self.messageHandler) # Assigning our thread to the connection handler function
			messageThread.daemon = True # Allowing exiting without closing threads
			messageThread.start() # Running the thread

	def getHandshake(self):
		data = self.connection.recv(1024)
		self.debug('Connection', 'Receiving Handshake')

		if data[0:1] == b'\x00':
			self.setSeed(str(data[1:], 'utf-8'))
			self.debug('Connection', 'Seed',str(data[1:], 'utf-8'))
		else:
			sys.exit()

		self.connection.send(b'\x01' + bytes(str(self.getSeed()), 'utf-8'))
		self.debug('Connection', 'Sending Handshake')

		self.debug('Connection', 'Handshake Successfull')

		return True
 
	def recvall(self, connection):
		chunk = connection.recv(1024)
		while chunk:
			yield chunk
			if len(chunk) < 1024:
				break
			chunk =  self.connection.recv(1024)

	def run(self):
		self.debug('Main', 'Client Running')
		while self.running == True:
			message = b''.join(self.recvall(self.connection))
			self.debug('Main', 'Message Received', message)
			temp = str(message, 'utf-8')
			print(Rose(self.getSeed()).decrypt(temp))

class Rose():

	seed = 0

	def __init__(self, seed = None):
		if seed != None:
			self.setSeed(seed)
		else:
			self.setSeed(self.seed)

	def setSeed(self, seed):
		self.seed = self.generateSeed(seed)

	def getSeed(self):
		return self.seed

	def generateSeed(self, bud):
		seedPod = []

		for seed in str(bud):
			seedPod.append(str(self.randomInt(ord(seed), (ord(seed) * ord(seed)))))

		temp = int(''.join(seedPod))

		return (temp * self.randomInt(temp, temp * temp) * 0xffff)

	def random(self):
		seed = (self.seed + 0xe120fc15)
		temp = (seed * 0x4a39b704)
		seed = (temp >> 32) ^ temp
		temp = (seed * 0x12fad5c9)
		seed = (temp >> 32) ^ temp
		return seed

	def randomInt(self, min, max):
		return ((self.random() % (max - min)) + min)

	def encrypt(self, data):
		string = ''
		for char in data:
			temp = int(ord(char)) * self.getSeed()
			string = f'{string}-{str(temp)}'
		
		return string[1:]

	def decrypt(self, data):
		string = ''
		data = data.split('-')
		for char in data:
			temp = int(int(char) / self.getSeed())
			string = f'{string}{chr(temp)}'

		return string

# KEY:
# \x00 : Handshake
# \x01 : Reverse Handshake
# \x02 : User Name

def main():
	if len(sys.argv) > 1:
		if sys.argv[1] == '--client' or sys.argv[1] == '-c':
			Client(None, None).run() # Define the Client

		if sys.argv[1] == '--server' or sys.argv[1] == '-s':
			Server(None, None, 'ThisIsATestSeed01010101').run() # Define the Server

		if sys.argv[1] == '--help' or sys.argv[1] == '-h':
			print('mehChat - A Terminal based chat application')
			print('--c | --client	| to run as a client')
			print('--s | --server	| to run as a server')
			print('--h | --help	| for a list of arguments')
	else:
		print('mehChat - A Terminal based chat application')
		print('--help | -h for a list of arguments')

if __name__ == "__main__":
	main()
