from PyQt5.QtCore import *
from PyQt5.QtNetwork import *
import json
from src.utils.utils import *
import logging

# HOST='127.0.0.1'
# PORT=8000
HOST	=	'cbhome-dev-server-socket.sugadev.top'
PORT	=	3002

class socketClient (QThread):
	uplinkSignal=pyqtSignal(dict, name="uplinkSignal")
	downlinkSignal=pyqtSignal(dict, name="downlinkSignal")

	def __init__(self):
		super(socketClient, self).__init__()
		self.uplinkSignal.connect(self.uplink)
		self.tcpSocket=QTcpSocket()
		self.tcpSocket.setSocketOption(QTcpSocket.KeepAliveOption, QVariant(1))
		self.tcpSocket.readyRead.connect(self.on_ready_read)
		self.tcpSocket.connected.connect(self.on_connected)
		self.tcpSocket.disconnected.connect(self.on_disconnect)
		self.tcpSocket.error.connect(self.on_error)
		self.connectToHost(HOST,PORT)

	def connectToHost(self, host, port):
		try:
			self.tcpSocket.close()
		except:
			pass
		self.tcpSocket.connectToHost(host, port)

	def close(self):
		self.disconnectFromHost()

	def send(self, data):
		self.tcpSocket.writeData('%s|%s' % (len(data), data))

	def on_ready_read(self):
		if self.tcpSocket.bytesAvailable():
			data = self.tcpSocket.readAll().data().decode('utf-8')
			try:
				print(parseMessage(instr=data))
				self.downlinkSignal.emit(json.loads(parseMessage(instr=data)))
			except Exception as e:
				print(e)

	def print_command(self, data):
		print('data!')

	def get_sstate(self):
		print(self.tcpSocket.state())
		if self.tcpSocket.state()!=3:
			self.connectToHost(HOST,PORT)

	def on_error(self):
		print('conntection to server:', self.tcpSocket.errorString())
		QTimer.singleShot(1000, self.do_reconnect)  # or any callable, slot is unnecessary

	pyqtSlot()
	def do_reconnect(self):
		self.connectToHost(HOST, PORT)

	def on_disconnect(self):
		print('disconnected!')

	def on_connected(self):
		print('connected!')

	def tick(self):
		self.downlinkSignal.emit({"id": 123456})

	def uplink(self,data):
		print("uplink send to server:",data)

	def run(self):
		self.exec_()
