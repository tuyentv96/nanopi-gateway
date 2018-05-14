#! /usr/bin/python
# a simple tcp server
import socket,os,json,time
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('0.0.0.0', 8000))
sock.listen()
data={
    "id": "unique_string",
    "type": 1002,
    "data": {
        "values": {
            "1": 1
        }
    }
}
data2={
    "id": "unique_string",
    "type": 1002,
    "data": {
        "values": {
            "1": 0
        }
    }
}
while True:
    connection,address = sock.accept()
    while True:
        try:
            connection.send(json.dumps(data).encode())
            time.sleep(1)
            connection.send(json.dumps(data1).encode())
            time.sleep(1)
        except:
            pass
        time.sleep(1)
    buf = connection.recv(1024)
    print(buf)
    connection.send(buf)
    connection.close()