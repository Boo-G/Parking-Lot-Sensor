import paho.mqtt.client as mqtt
import time
import RPi.GPIO as GPIO

# Button/Sensor GPIOs
BtnPin = 13
Rpin = 12
Gpin = 11
TRIG = 18
ECHO = 16
# Parking Lot GPIOs
Lot1, Lot2, Lot3, Lot4, Lot5 = 29, 31, 33, 35, 37

greenFlag, redFlag = 0, 1
dataMessage = None


##################################################
# Subscriber
##################################################

# Callback function for message reception
def on_message(client, userdata, message):
    global dataMessage
    dataMessage = message.payload.decode("utf-8")
    LEDState(dataMessage)
    print("message received:", dataMessage)

# Subscribe to receive messages
def subscribe():
    client.loop_start()
    client.subscribe("design3_bcg009")  # topic
    client.on_message = on_message
    print("subscribed")


##################################################
# Publisher
##################################################

# Function to handle button press event
def buttonPress(channel):
    global greenFlag, redFlag
    holder1 = time.time()

    if greenFlag == 0:
        # set green on, and start sending distanstce
        greenFlag = 1
        redFlag = 0
        GPIO.output(Rpin, 0)
        GPIO.output(Gpin, 1)
        currentDistance = distance()
        print(currentDistance, 'cm')
        print('')
        publish(currentDistance)

    if redFlag == 0:
        # Set red on, and send a reminder to the user every 5 seconds
        greenFlag = 0
        redFlag = 1
        GPIO.output(Rpin, 1)
        GPIO.output(Gpin, 0)
        holder2 = time.time()
        overlap = holder2 - holder1
        if overlap >= 5:
            print("Press the switch to enable the Ultrasonic")
            holder1 = time.time()
            holder2 = time.time()



# Publish message
def publish(data):
    time.sleep(1)
    client.publish("design3_bcg009_sensor", data)

# Function to flicker LEDs
def flicker():
    GPIO.output(Rpin, 1)
    GPIO.output(Gpin, 0)
    time.sleep(1)
    GPIO.output(Rpin, 0)
    GPIO.output(Gpin, 0)
    time.sleep(1)
    GPIO.output(Rpin, 1)
    GPIO.output(Gpin, 0)

# LEDState function
def LEDState(out_message):
    global dataMessage, greenFlag, redFlag
    greenFlag, redFlag = 0, 1

    if dataMessage == "1": 
        # The ultrasonic sensor has been disabled
        flicker()

    if dataMessage == "0":
        # The ultrasonic sensor has been enabled
        GPIO.output(Rpin, 0)
        GPIO.output(Gpin, 1)

# Function to detect parking lot state
def lotDetected(channel):
    lotData = ' '.join(str(GPIO.input(lot)) for lot in [Lot1, Lot2, Lot3, Lot4, Lot5])
    publish(lotData)

# Setup GPIO and Ultrasonic sensor
def setup():
    global greenFlag, redFlag
    greenFlag, redFlag = 0, 1
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(Gpin, GPIO.OUT)
    GPIO.setup(Rpin, GPIO.OUT)
    GPIO.setup(Lot1, GPIO.IN)
    GPIO.setup(Lot2, GPIO.IN)
    GPIO.setup(Lot3, GPIO.IN)
    GPIO.setup(Lot4, GPIO.IN)
    GPIO.setup(Lot5, GPIO.IN)
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)
    GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BtnPin, GPIO.RISING, callback=buttonPress, bouncetime=200)
    GPIO.add_event_detect(Lot1, GPIO.BOTH, callback=lotDetected, bouncetime=1)
    GPIO.add_event_detect(Lot2, GPIO.BOTH, callback=lotDetected, bouncetime=1)
    GPIO.add_event_detect(Lot3, GPIO.BOTH, callback=lotDetected, bouncetime=1)
    GPIO.add_event_detect(Lot4, GPIO.BOTH, callback=lotDetected, bouncetime=1)
    GPIO.add_event_detect(Lot5, GPIO.BOTH, callback=lotDetected, bouncetime=1)

# Function to measure distance using Ultrasonic sensor
def distance():
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
    final = during * 340 / 2 * 100  # distance in cm
    publish(final)
    return final

# Main loop
def loop():
    subscribe()
    while True:
        distance()

# Cleanup GPIO on program exit
def destroy():
    GPIO.output(Gpin, GPIO.HIGH)
    GPIO.output(Rpin, GPIO.HIGH)
    GPIO.cleanup()

if __name__ == '__main__':
    setup()
    mqttBroker = "broker.hivemq.com"
    client = mqtt.Client("fake_temp3")
    client.connect(mqttBroker)

    try:
        GPIO.output(Gpin, 0)
        GPIO.output(Rpin, 0)
        loop()
    except KeyboardInterrupt:
        destroy()
