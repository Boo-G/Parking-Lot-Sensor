import paho.mqtt.client as mqtt
import time
from cryptography.fernet import Fernet
#!/usr/bin/env python3
from pickletools import read_float8
import RPi.GPIO as GPIO

BtnPin = 13
Rpin   = 12
Gpin   = 11
TRIG = 18
ECHO = 16
# Parking Lot GPIOs
Lot1 = 29
Lot2 = 31
Lot3 = 33
Lot4 = 35
Lot5 = 37

############################################################################################################
# Subscriber
##################################################

# Callback function
def on_message(client, userdata, message):
    global b 
    b = message.payload.decode("utf-8")
    test(b)
    msg_list = b.split() 
    print("message recieved:", b)

def subscribe():


    # subscribe to recieve a message
    client.loop_start()
    client.subscribe("design3_bcg009") # topic
    client.on_message = on_message # call a function
    print("sub")
    # time.sleep(50)

##################################################################################################################
# Publisher
##############################################################
def buttonPress(self):
	holder1 = time.time()

	if (greenFlag == 0):
		print("IM GREEN")
		greenFlag = 1
		redFlag = 0

	if (redFlag == 0):
		print("IM RED")
		greenFlag = 0
		redFlag = 1

	if greenFlag == 1:
		GPIO.output(Rpin, 0)
		GPIO.output(Gpin, 1)
		dis = distance()
		print (dis, 'cm')
		print ('')
		publish(dis)
		# time.sleep(0.3)
		print("Press the switch to disable the Ultrasonic")
		pass

	if redFlag == 1:
		GPIO.output(Rpin, 1)
		GPIO.output(Gpin, 0)
		holder2 = time.time()
		overlap = holder2 - holder1
		if overlap >= 5:
			print("Press the switch to enable the Ultrasonic")
			holder1 = time.time()
			holder2 = time.time()

def publish(data):
    #publish message
	time.sleep(1)
	client.publish("design3_bcg009_sensor", data)

def flicker():
    # Turn red
	GPIO.output(Rpin, 1)
	GPIO.output(Gpin, 0)
	time.sleep(1)
    # Turn off
	GPIO.output(Rpin, 0)
	GPIO.output(Gpin, 0)
	time.sleep(1)
	GPIO.output(Rpin, 1)
	GPIO.output(Gpin, 0)

def test(out_message):
	holder1 = time.time()
	greenFlag = 0
	redFlag = 1

	if(b == "1"):
		print("MADE IT TO B")
		flicker()

	if(b == "0"):
		# while(True):
		GPIO.output(Rpin, 0)
		GPIO.output(Gpin, 1)
		# dis = distance()
		# print (dis, 'cm')
		# print ('')
		# publish(dis)
        #needs delay for while

def lotDetected(self):
	lotData = str(GPIO.input(Lot1))+' '+str(GPIO.input(Lot2))+' '+str(GPIO.input(Lot3))+' '+str(GPIO.input(Lot4))+' '+str(GPIO.input(Lot5))
	publish(lotData)


def setup():
	global greenFlag
	global redFlag
	greenFlag = 0
	redFlag = 1
	GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
	GPIO.setup(Gpin, GPIO.OUT)     # Set Green Led Pin mode to output
	GPIO.setup(Rpin, GPIO.OUT)     # Set Red Led Pin mode to output
	GPIO.setup(Lot1, GPIO.IN)
	GPIO.setup(Lot2, GPIO.IN)
	GPIO.setup(Lot3, GPIO.IN)
	GPIO.setup(Lot4, GPIO.IN)
	GPIO.setup(Lot5, GPIO.IN)
	GPIO.setup(TRIG, GPIO.OUT)
	GPIO.setup(ECHO, GPIO.IN)
	GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set BtnPin's mode is input, and pull up to high level(3.3V)
	GPIO.add_event_detect(BtnPin, GPIO.RISING, callback=buttonPress, bouncetime=200)
	GPIO.add_event_detect(Lot1, GPIO.BOTH, callback=lotDetected, bouncetime=1)
	GPIO.add_event_detect(Lot2, GPIO.BOTH, callback=lotDetected, bouncetime=1)
	GPIO.add_event_detect(Lot3, GPIO.BOTH, callback=lotDetected, bouncetime=1)
	GPIO.add_event_detect(Lot4, GPIO.BOTH, callback=lotDetected, bouncetime=1)
	GPIO.add_event_detect(Lot5, GPIO.BOTH, callback=lotDetected, bouncetime=1)

def distance():
	# Ultra sonic sensor grab distance in relation to it
	GPIO.output(TRIG, 0)
	time.sleep(0.000002)

	GPIO.output(TRIG, 1)
	time.sleep(0.00001)
	GPIO.output(TRIG, 0)

	while GPIO.input(ECHO) == 0:
		a = 0
	time1 = time.time()
	while GPIO.input(ECHO) == 1:
		a = 1
	time2 = time.time()

	during = time2 - time1

	final = during * 340 / 2 * 100 # distance in cm
	publish(final)


def loop():
	subscribe()
	while True:
		distance()

def destroy():
	GPIO.output(Gpin, GPIO.HIGH)       # Green led off
	GPIO.output(Rpin, GPIO.HIGH)       # Red led off
	GPIO.cleanup()                     # Release resource

if __name__ == '__main__':     # Program start from here
	setup()
	#use a public brpker, declare objects/methods
	mqttBroker = "broker.hivemq.com" # public broker
	client = mqtt.Client("fake_temp3") # your name as client
	client.connect(mqttBroker)

	try:
		GPIO.output(Gpin, 0)       # Green led off
		GPIO.output(Rpin, 0)       # Red led off
		loop()
	except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
		destroy()
