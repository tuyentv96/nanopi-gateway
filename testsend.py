
import socket
import sys
import threading
import time
import json
class sendUpdateSensor (threading.Thread):
   def __init__(self, socketClient):
      threading.Thread.__init__(self)
      self.s = socketClient

   def run(self):
      print("Starting")
      time.sleep(1)
      while True:
          # print str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+ ": updating sensor"
          self.s.send("@UPDATE;authen_key;S:1:temp=11.2,hum=2.23,moi=3.12,co2=4.23,lux=5.2,ph=6.44,ec=7.9;#\n")
          time.sleep(10)


HOST = '192.168.10.182'    # The remote host
PORT = 3000              # The same port as used by the server
for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        s = socket.socket(af, socktype, proto)
    except socket.error as msg:
        s = None
        continue
    try:
        s.connect(sa)
    except socket.error as msg:
        s.close()
        s = None
        continue
    break
if s is None:
    print('could not open socket')
    sys.exit(1)
while True:
    data = {
        "id": "unique_string",
        "type": 1002,
        "imei": "DC4F2225FBD1",
        "data": {
            "values": {
                "2": 1
            }
        }
    }
    x='|30#'+json.dumps(data)
    s.send(x.encode())
    time.sleep(1)
