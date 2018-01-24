#! /usr/bin/python

import sys
import serial
from PyQt5.QtCore import *
import RPi.GPIO as GPIO
import person_pb2
from src.mqtt import MQTTConnection,topic
import user_pb2
from src.constants import constant
import json

class TimerThread(QThread):
	update = pyqtSignal()

	def __init__(self, event):
		QThread.__init__(self)
		self.stopped = event

	def run(self):
		while not self.stopped.wait(0.02):
			self.update.emit()
			
class uartThread(QThread):
	updateUartData=pyqtSignal(dict,name="updateUartData")
	
	def __init__(self):
		super(uartThread, self).__init__()
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(16,GPIO.OUT)
		GPIO.setup(18,GPIO.OUT)
		GPIO.output(16,False)
		GPIO.output(18,False)
	
		self.ser = serial.Serial(
			port='/dev/ttyS1',
			baudrate = 115200,
			parity=serial.PARITY_NONE,
			stopbits=serial.STOPBITS_ONE,
			bytesize=serial.EIGHTBITS,
			timeout=1
		)
		# self.ser = serial.Serial('/dev/ttyS1',115200)
		self.sendTest = QTimer(self)
		self.sendTest.timeout.connect(self.tick)
		# self.ser.close()
		# self.ser.open()
		#self.sendTest.start(2000)
		self.sendTest1 = QTimer(self)
		self.sendTest1.timeout.connect(self.tick1)
		# self.ser.close()
		# self.ser.open()
		#self.sendTest1.start(60001)
	def makeSignalConnection(self,Obj):
		Obj.receiveData.connect(self.sendUartData)
	def sendUartData(self,data):
		self.write(data)
		print("send via uart",data)
	def tick(self):
		data="@ZBS=00124B0005A9905C;t:24;h:30;l:100!"
		data1="@ZBC=00124B0004E77B07;31!"
		for i in self.uartHandle(data):
			self.updateUartData.emit(i)
		for i in self.uartHandle(data1):
			self.updateUartData.emit(i)
	def tick1(self):
		data="@ZBS=00124B0005A9905C;t:25;h:31;l:100!"
		data1="@ZBC=00124B0004E77B07;30!"
		for i in self.uartHandle(data):
			self.updateUartData.emit(i)
	def uartHandle(self,str):
		retArray=[]
		startIndex=str.find("@")
		stopIndex=str.find("!")
		while startIndex>=0 and stopIndex>startIndex:
			print(str[startIndex + 1:stopIndex])
			x=self.parseSensor(str[startIndex + 1:stopIndex])
			print(x)
			if x!=None:
				retArray.append(x)
			#print(str)
			str=str[stopIndex+1:]
			startIndex = str.find("@")
			stopIndex = str.find("!")
		return retArray
	def parseSensor(self,str):
		params=str.split(";")
		if "ZBS" in params[0]:
			cmd=params[0][:str.find("=")]
			code=str[str.find("=")+1:str.find(";")]
			temp=params[1][2:]
			humd=params[2][2:]
			lux=params[3][2:]
			return {"cmd":cmd,"code":code,"temp":int(temp),"humd":int(humd),"lux":int(lux)}
		if "ZBC" in params[0]:
			cmd=params[0][:str.find("=")]
			code=str[str.find("=")+1:str.find(";")]
			pos=params[1][:1]
			status=params[1][1:]
			print(cmd,code,pos,status)
			return {"cmd":cmd,"code":code,"pos":int(pos),"status":int(status)}
		return None
	def run(self):
		print("Started")
		buffer = ""
		while True:
			data = self.ser.readline()
			# if data:
			#     char = data.decode('ascii')
			#     if char=="\n":
			#         print("raw: "+buffer)
			#         params=buffer.split(";")
			#         if params[0]=="@sensor":
			#             self.updateSensorSignal.emit(int(params[1]),int(params[2]))
			#         buffer=""
			#     else:
			#         buffer=buffer+char
			if data:
				data=data.decode('ascii')
				print(data)
				for i in self.uartHandle(data):
					self.updateUartData.emit(i)
	def write(self,data):
		print("Send to Cordinator",data)
		#print("@ZB+CT=00124B0004E77B07;21!".encode('ascii'))
		#self.tick()
		self.ser.write(data.encode('ascii'))

# mqttThread create mqtt connection to mqtt server
class mqttThread (QThread):
	receiveData=pyqtSignal(str,name="receiveData")
	def __init__(self):
		super(mqttThread, self).__init__()
		self.keepRunning = True
		self.serial="1234"
		self.data_latest = 0
		self.checkConnectionTimerDuration=3000

		self.checkConnectionTimer = QTimer(self)
		self.checkConnectionTimer.timeout.connect(self.tick)
		self.checkConnectionTimer.start(self.checkConnectionTimerDuration)
		# self.start()

		self.sendDataTimer = QTimer(self)
		self.sendDataTimer.timeout.connect(self.sendData)
		#self.sendDataTimer.start(2000)
	def makeSignalConnection(self,uartObj):
		uartObj.updateUartData.connect(self.sendSensor)
	def run(self):
		self.connect()
		
	@pyqtSlot(int,int)
	def sendSensor(self,data):
		print("uart rev: {}".format(data))
		payload={}
		if data["cmd"]=="ZBS":
			payload['code']=data["code"]
			payload['temp']=data["temp"]
			payload['humd']=data["humd"]
			payload['lux']=data["lux"]
			sendTopic=topic.deviceTopic(constant.appID,data["code"],constant.uplink,constant.sensor)

		if data["cmd"]=="ZBC":
			payload['code']=data["code"]+"-"+str(data["pos"])
			# payload['pos']=data["pos"]
			payload['status']=data["status"]
			sendTopic=topic.deviceTopic(constant.appID,payload['code'],constant.uplink,"control")
		print("command {} with payload:{}".format(data["cmd"],payload))
		json.dumps(payload)
		self.publish(topic.generateTopic(sendTopic),json.dumps(payload))
	def sendData(self):
		if self.mqttc.connected==True:
			user = user_pb2.User()
			user.id = "123"
			user.password = "456"
			#print(user.SerializeToString())
			sendTopic=topic.deviceTopic(constant.appID,constant.devID,constant.uplink,constant.sensor)
			self.mqttc.publish(topic.generateTopic(sendTopic),user.SerializeToString())
	def publish(self,topic,msg):
		self.mqttc.publish(topic,msg)
	def connect(self):
		try:
			self.mqttc.keepRunning=False
		except:
			print(None)
		self.mqttc=MQTTConnection.mqttConnectClass()
		self.mqttc._mqttc.on_message = self.mqttOnMessage
		self.mqttc._mqttc.on_connect = self.mqttOnConnect
		self.mqttc._mqttc.on_disconnect = self.mqttOnDisconnect
		self.mqttc.start()
		# self.mqttc2=MQTTConnection.mqttConnectClass2()
		# self.mqttc2.start()
	def tick(self):
		try:
			if self.mqttc.connected==False:
				print("Try connect")
				self.connect()
			else:
				return None
		except:
			self.connect()


	def mqttOnConnect(self, mqttc, obj, flags, rc):
		print("on connect with rc: "+str(rc))
		self.mqttc.connected=True
		self.mqttc.subscribe("smarthome/device/+/event/control")
		#self.Is_Connected()

	def mqttOnDisconnect(self,client, userdata, rc):
		print("disconnect")
		self.mqttc.connected=False
		self.mqttc.keepRunning=False
		self.mqttc._mqttc.loop_stop()
		self.data_latest = 0


	def mqttOnMessage(self, mqttc, obj, msg):
		self.data_latest = 0
		print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload.decode("utf-8")))
		deviceTopic=topic.parseDeviceTopic(msg.topic)
		print("DV",deviceTopic.field)
		if deviceTopic.field=="control":
			try:
				j = json.loads(str(msg.payload.decode("utf-8")))
				code=j["code"]
				status=j["status"]
				x=code.find("-")
				baseCode=code[:x]
				addr=code[x+1:]
				data="@ZB+CT={};{}!\r\n".format(baseCode,addr+str(status))
				self.receiveData.emit(data)
				print(data)
			except:
				print("parsejson err")
class mainThread (QThread):
	def __init__(self):
		super(mainThread, self).__init__()
		self.mMQTTThread = mqttThread()
		self.mUartThread = uartThread()
		self.mMQTTThread.makeSignalConnection(self.mUartThread)
		self.mUartThread.makeSignalConnection(self.mMQTTThread)
		self.mMQTTThread.start()
		self.mUartThread.start()

def main():
	app = QCoreApplication(sys.argv)
	mMainThread = mainThread()
	mMainThread.start()
	sys.exit(app.exec_())

main()

