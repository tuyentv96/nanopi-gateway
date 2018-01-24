#!/usr/bin/python

# this source is part of my Hackster.io project:  https://www.hackster.io/mariocannistra/radio-astronomy-with-rtl-sdr-raspberrypi-and-amazon-aws-iot-45b617

# use this program to test the AWS IoT certificates received by the author
# to participate to the spectrogram sharing initiative on AWS cloud

# this program will publish test mqtt messages using the AWS IoT hub
# to test this program you have to run first its companion awsiotsub.py
# that will subscribe and show all the messages sent by this program

import paho.mqtt.client as paho
import os
import socket
import ssl
from time import sleep
from random import uniform
import socket
connflag = False
import sys
from PyQt5.QtCore import *
def on_connect(client, userdata, flags, rc):
    global connflag
    connflag = True
    print("Connection returned result: " + str(rc) )

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

#def on_log(client, userdata, level, buf):
#    print(msg.topic+" "+str(msg.payload))

class mqttConnectClass (QThread):
    def __init__(self):
        mqttc = paho.Client()
        mqttc.on_connect = on_connect
        mqttc.on_message = on_message
        #mqttc.on_log = on_log
        
        # awshost = "ttnvn.com"
        awshost=socket.gethostbyname('ttnvn.com')
        awsport = 8883
        clientId = "myThingName"
        thingName = "myThingName"
        caPath = "ca-cert.pem"
        certPath = "client-cert.pem"
        keyPath = "client-key.pem"
        print(caPath)
        print(certPath)
        print(keyPath)
        mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
        
        mqttc.connect(awshost, awsport, keepalive=60)
        
        def on_disconnect(client, userdata, rc):
            if rc != 0:
                print("Unexpected disconnection.")
        mqttc.loop_start()
        
        while 1==1:
            sleep(0.5)
            if connflag == True:
                tempreading = uniform(20.0,25.0)
                mqttc.publish("temperature", tempreading, qos=1)
                print("msg sent: temperature " + "%.2f" % tempreading )
            else:
                print("waiting for connection...")
app = QCoreApplication(sys.argv)
mMainThread = mqttConnectClass()
mMainThread.start()
sys.exit(app.exec_())