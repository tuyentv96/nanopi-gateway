#!/usr/bin/python

import logging
import logging.handlers
import argparse
import time
from bluetooth import *
import subprocess
import json
from PyQt5.QtCore import *
import sys
import netifaces as ni
from src.constants import constant
import nopin
import socket
class LoggerHelper(object):
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message.rstrip() != "":
            self.logger.log(self.level, message.rstrip())


def setup_logging():
    # Default logging settings
    LOG_FILE = "/var/log/raspibtsrv.log"
    LOG_LEVEL = logging.INFO

    # Define and parse command line arguments
    argp = argparse.ArgumentParser(description="Raspberry PI Bluetooth Server")
    argp.add_argument("-l", "--log", help="log (default '" + LOG_FILE + "')")

    # Grab the log file from arguments
    args = argp.parse_args()
    if args.log:
        LOG_FILE = args.log

    # Setup the logger
    logger = logging.getLogger(__name__)
    # Set the log level
    logger.setLevel(LOG_LEVEL)
    # Make a rolling event log that resets at midnight and backs-up every 3 days
    handler = logging.handlers.TimedRotatingFileHandler(LOG_FILE,
        when="midnight",
        backupCount=3)

    # Log messages should include time stamp and log level
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    # Attach the formatter to the handler
    handler.setFormatter(formatter)
    # Attach the handler to the logger
    logger.addHandler(handler)

    # Replace stdout with logging to file at INFO level
    sys.stdout = LoggerHelper(logger, logging.INFO)
    # Replace stderr with logging to file at ERROR level
    sys.stderr = LoggerHelper(logger, logging.ERROR)


class bluetoothServer (QThread):
    def __init__(self):
        super(bluetoothServer, self).__init__()
        print("hello")
    def run(self):
        # We need to wait until Bluetooth init is done
        time.sleep(3)

        # Make device visible
        #os.system("hciconfig hci0 piscan")

        # Create a new server socket using RFCOMM protocol
        self.server_sock = BluetoothSocket(RFCOMM)
        # Bind to any port
        self.server_sock.bind(("", PORT_ANY))
        # Start listening
        self.server_sock.listen(1)

        # Get the port the server socket is listening
        port = self.server_sock.getsockname()[1]

        # The service UUID to advertise
        uuid = "7be1fcb3-5776-42fb-91fd-2ee7b5bbb86d"

        # Start advertising the service
        advertise_service(self.server_sock, "RaspiBtSrv",
                        service_id=uuid,
                        service_classes=[uuid, SERIAL_PORT_CLASS],
                        profiles=[SERIAL_PORT_PROFILE])

        # These are the operations the service supports
        # Feel free to add more
#        print("started server")
        # Main Bluetooth server loop
        while True:

            print("Waiting for connection on RFCOMM channel %d" % port)

            try:
                client_sock = None

                # This will block until we get a new connection
                client_sock, client_info = self.server_sock.accept()
                print("Accepted connection from ", client_info)
                buffer = ""
                ni.ifaddresses('wlan0')
                ip = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']
                client_sock.send(ip)
                while True:
                    data = client_sock.recv(1024)
                    if data:
                        try:
                            jsonStr=data.decode("utf-8")
                            print(jsonStr)
                            j = json.loads(jsonStr)
                            print(j["ssid"],j["password"])
                            connectState=wifiConnect(j["ssid"],j["password"])
                            if connectState==True:
                                try:
                                    ip = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']
                                    client_sock.send(ip)
                                except Exception as e:
                                    print(e)
                                
                        except Exception as e:
                            print(e)
                            print("Fail")
                        #client_sock.send(data) # Echo back to client

            except IOError as e:
                print(e)
                pass

            except KeyboardInterrupt as e:
                print(e)
                if client_sock is not None:
                    client_sock.close()

                self.server_sock.close()

                print("Server going down")
                break

# Main loop
def main():
    # Setup logging
#    setup_logging()
#    run_event = threading.Event()
#    run_event.set()
    time.sleep(20)
    app = QCoreApplication(sys.argv)
    t1=nopin.activeBluetooth()
    t1.start()
    thread2 = bluetoothServer()
    thread2.start()
    sys.exit(app.exec_())
    

def wifiConnect(name,pwd):
    #ret=os.system("nmcli dev wifi connect '{}' password '{}'".format(name,pwd))

    proc = subprocess.Popen("nmcli dev wifi connect '{}' password '{}'".format(name,pwd), stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()

    print("program output:", out)
    if "successfully" in str(out):
        print("Connect succcess")
        return False
    else:
        print ("Connect fail")
        return True
main()
