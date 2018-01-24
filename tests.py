import serial
import time
#ser = serial.Serial('/dev/ttyS1',115200)
ser = serial.Serial('/dev/ttyS1', 115200)
a=0
    # data='@ZB+CT=00124B0004E77B07;21!!\r\n'.encode()
data="@ZB+CT=00124B0004E77B07;21!"
ser.flushInput()
print(ser.write(b"@ZB+CT=00124B0004E77B07;21!"))
while True:

    #print(data)
    # print(ser.inWaiting())
    reading = ser.read(ser.in_waiting)
    if reading:
        try:
            print("RV",reading.decode('ascii'))
        except:
            print("ERR")
    # time.sleep(1)
