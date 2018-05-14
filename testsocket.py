
import socket
import sys
import threading
import time
import json

HOST = '192.168.50.1'    # The remote host
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
    # data={
    #     "id": "unique_string",
    #     "type": 1002,
    #     "data": {
    #         "values": {
    #             "1": 1,
    #             "2": 1,
    #             "3": 1,
    #             "4": 1
    #
    #         }
    #     }
    # }
    # s.sendall(bytes(json.dumps(data), encoding='ascii'))
    # #s.close()
    # time.sleep(1)
    data = s.recv(1024)
    if data!=None:
        print(data)
