from PyQt5.QtCore import *
from PyQt5.QtNetwork import *
import json
from src.utils.utils import *
import logging

HOST='0.0.0.0'
PORT=3000

class HandleSocketClient(QThread):
    removeSignal = pyqtSignal(str, name="removeSignal")
    uplinkSignal = pyqtSignal(dict, name="uplinkSignal")
    downlinkSignal = pyqtSignal(dict, name="downlinkSignal")

    def __init__(self,clientConnection):
        super(HandleSocketClient, self).__init__()
        self.clientConnection=clientConnection
        self.clientConnection.readyRead.connect(self.receiveMessage)
        self.downlinkSignal.connect(self.receiveMessage)
        self.clientConnection.disconnected.connect(self.removeConnection)

    def send(self,data):
        dataWrite=json.dumps(data,separators=(',', ':'))
        dataWrite=('{}{}'.format('|'+str(len(dataWrite))+'#',dataWrite))
        self.sendMessage(dataWrite)

    def run(self):
        self.exec_()
    def stop(self):
        self.quit()
        self.wait(2000)
    def sendMessage(self, text):
        print("send message:",text)
        self.clientConnection.write(bytes(text, encoding='ascii'))
    def receiveMessage(self):
        if self.clientConnection.bytesAvailable() > 0:
            rawData = self.clientConnection.readAll()
            instr = str(rawData, encoding='ascii')
            print(instr)
            try:
                # prefix=instr.find('|')
                # delimiter=instr.find('#')
                # if prefix<0 or delimiter<0:
                #     print("wrong format")
                #     return
                data = json.loads(parseMessage(instr))
                # self.sendMessage(json.dumps(data))
                self.uplinkSignal.emit(data)
            except:
                print("parse json error")

    def removeConnection(self):
        self.removeSignal.emit(self.clientConnection.socketID)

class SocketServer(QThread):
    uplinkSignal = pyqtSignal(dict, name="uplinkSignal")
    downlinkSignal = pyqtSignal(dict, name="downlinkSignal")

    def __init__(self):
        super(SocketServer, self).__init__()
        self.connections = []
        self.numConnection=0
        self.tcpServer = QTcpServer(self)
        self.tcpServer.listen(QHostAddress(HOST), PORT)
        self.tcpServer.newConnection.connect(self.addConnection)
        self.mutex=QMutex()

        self.downlinkSignal.connect(self.receiveMessage)

    def addConnection(self):
        self.mutex.lock()
        clientConnection = self.tcpServer.nextPendingConnection()
        self.numConnection=+1
        clientConnection.socketID=randomString(15)
        handleConn=HandleSocketClient(clientConnection)
        handleConn.removeSignal.connect(self.removeConnection)
        handleConn.uplinkSignal.connect(self.sendMessage)

        handleConn.setTerminationEnabled(True)
        handleConn.start()
        self.connections.append(handleConn)
        self.mutex.unlock()

    def receiveMessage(self,msg):
        print("msg:",msg)
        for c in self.connections:
            c.send(msg)

    def sendMessage(self, msg):
        print("msg:", msg)
        print(msg['id'])
        self.uplinkSignal.emit(msg)


    def removeConnection(self,socketID):
        self.mutex.lock()
        for c in self.connections:
            if c.clientConnection.socketID==socketID:
                self.numConnection =-1
                c.removeSignal.disconnect()
                c.uplinkSignal.disconnect()
                c.stop()
                self.connections.remove(c)
        self.mutex.unlock()
        print("num connections:",len(self.connections))




