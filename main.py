#! /usr/bin/python

from src.socketserver.socketserver import *
from src.socketclient.socketclient import *
import sys

class mainThread (QThread):
	def __init__(self):
		super(mainThread, self).__init__()
		self.mSocketClient = socketClient()
		self.mSocketServer = SocketServer()
		self.mSocketClient.downlinkSignal.connect(self.downlink)
		self.mSocketServer.uplinkSignal.connect(self.uplink)

		self.mSocketClient.start()
		self.mSocketServer.start()
	def downlink(self, data):
		print("downlink:",data)
		type=data['type']

		'''Update device values'''
		if type==1002:
			print("Update device values:",type)
		self.mSocketServer.downlinkSignal.emit(data)

	def uplink(self, data):
		print("uplink:", data)
		print(data['id'])
		response={}
		response['id']		=	data['id']
		response['type']	=	data['type']
		response['imei']	=	data['imei']
		response['error']	=	0

		if data['type']==1001:
			self.mSocketServer.downlinkSignal.emit(response)

		if data['type']==1002:
			self.mSocketServer.downlinkSignal.emit(response)
		self.mSocketClient.uplinkSignal.emit(data)


def main():
	app = QCoreApplication(sys.argv)
	mMainThread = mainThread()
	mMainThread.start()
	sys.exit(app.exec_())

main()

