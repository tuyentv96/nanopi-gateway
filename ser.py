import serial
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(16,GPIO.OUT)
GPIO.setup(18,GPIO.OUT)
GPIO.output(16,False)
GPIO.output(18,False)

ser = serial.Serial(
    port='/dev/ttyS1',
    baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)
print("Started")
buffer = ""
while True:
    data = ser.read()
    if data:
        char = data.decode('ascii')
        if char=="\n":
            print(buffer)
            buffer=""
        else:
            buffer=buffer+char
