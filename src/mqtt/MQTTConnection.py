import paho.mqtt.client as paho
import os
import socket
import ssl
from time import sleep
from random import uniform
import socket
connflag = False
from PyQt5.QtCore import *
import threading

def on_connect(client, userdata, flags, rc):
    global connflag
    connflag = True
    print("Connection returned result: " + str(rc) )

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    
class mqttConnectClass (threading.Thread):
    def __init__(self):
        super(mqttConnectClass, self).__init__()
        self._mqttc = paho.Client()
        #self._mqttc.on_publish = self.mqtt_on_publish
        self._mqttc.on_subscribe = self.mqtt_on_subscribe
        awshost='103.7.43.99'
        awsport = 1883
        #print(awsport)
        self.clientid="123"
        self.connected=False
        self.keepRunning=True

        pat=os.path.dirname(__file__)+"/"
        awshost='103.7.43.99'
        awsport = 8883
        clientId = "12345678"
        thingName = "myThingName"
        caPath = pat+"ca-cert.pem"
        certPath = pat+"client-cert.pem"
        keyPath = pat+"client-key.pem"
        print(awshost)
        print(caPath)
        print(certPath)
        print(keyPath)

        self._mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
        self._mqttc.connect(awshost, awsport, keepalive=60)
        

        self._mqttc.loop_start()
    def mqtt_on_publish(self, mqttc, obj, mid):
        print("mid: "+str(mid))
    def mqtt_on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: "+str(mid)+" "+str(granted_qos))
    def publish(self,topic,msg):
        self._mqttc.publish(topic,msg)
    def Sub_All(self):
        self._mqttc.subscribe("#", 0)
    def subscribe(self,topic):
        self._mqttc.subscribe(topic, 0)
    def run(self):
        try:
            print("DB0")
            self._mqttc.connect("103.7.43.99", 8883, 60)
            print("DB1")
            self.connected=True
        except:
            print("No connection")
            self.connected=False
            self.keepRunning = False
            return None

        self.keepRunning = True
        self._mqttc.loop_start()
        #self.Sub_All()
        # while self.keepRunning:
        #     self._mqttc.loop()
        rc = 0
        while rc == 0:
            rc = self._mqttc.loop_start()
        # return rc
        # while self.keepRunning:
        #     time.sleep(1)
        self.connected=False
        self.keepRunning = False
        print("Loop done !!!")

class mqttConnectClass2 (QThread):
    def __init__(self):
        self._mqttc = paho.Client()
        self._mqttc.on_connect = on_connect
        self._mqttc.on_message = on_message
        #mqttc.on_log = on_log
        
        # awshost = "ttnvn.com"
        pat=os.path.dirname(__file__)+"/"
        awshost=socket.gethostbyname('ttnvn.com')
        awsport = 8883
        clientId = "12345678"
        thingName = "myThingName"
        caPath = pat+"ca-cert.pem"
        certPath = pat+"client-cert.pem"
        keyPath = pat+"client-key.pem"
        print(caPath)
        print(certPath)
        print(keyPath)
        self._mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
        
        self._mqttc.connect(awshost, awsport, keepalive=60)
        
        def on_disconnect(client, userdata, rc):
            if rc != 0:
                print("Unexpected disconnection.")
        self._mqttc.loop_start()
        
        while 1==1:
            sleep(0.5)
            if connflag == True:
                tempreading = uniform(20.0,25.0)
                self._mqttc.publish("temperature", tempreading, qos=1)
                print("msg sent: temperature " + "%.2f" % tempreading )
            else:
                print("waiting for connection...")
    def run(self):
        print("done")
    def publish(self,topic,msg):
        self._mqttc.publish(topic,msg)
    def Sub_All(self):
        self._mqttc.subscribe("#", 0)
    def subscribe(self,topic):
        self._mqttc.subscribe(topic, 0)