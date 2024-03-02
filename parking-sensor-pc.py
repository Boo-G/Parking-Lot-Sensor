from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import smartParking_ui
from PyQt5.QtWidgets import QMessageBox
import paho.mqtt.client as mqtt

# Use a public broker, declare objects/methods
MQTT_BROKER = "broker.hivemq.com"  # Public broker
CLIENT = mqtt.Client("fake_temp1")  # Client instance
CLIENT.connect(MQTT_BROKER)

class SpotState:
    EMPTY = 0
    OCCUPIED = 1

class MainWindow(QtWidgets.QMainWindow, smartParking_ui.Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        # MQTT setup
        CLIENT.loop_start()
        CLIENT.subscribe("design3_bcg009_sensor")
        CLIENT.on_message = self.on_message

        # Connect GUI buttons to functions
        self.sendButton.clicked.connect(self.sendText)
        self.onButton.clicked.connect(self.warnOn)
        self.offButton.clicked.connect(self.warnOff)

    def on_message(self, client, userdata, message):
        # Callback function when a message is received
        data = message.payload.decode("utf-8")
        self.dataCheck(data)
        print("Message received:", data)

    def dataCheck(self, data):
        dataList = data.split()

        if len(dataList) > 1:
            # Handle parking spot data
            for i, spot in enumerate([self.spotOne, self.spotTwo, self.spotThree, self.spotFour, self.spotFive]):
                state = int(dataList[i])
                self.update_spot_display(spot, state)
        elif len(dataList) == 1:
            # Handle other data (e.g., sensor text)
            self.sensorText.setText(dataList[0])

    def update_spot_display(self, spot, state):
        # Update the display of a parking spot based on its state
        spot.setDigitCount(1)
        spot.display(SpotState.EMPTY if state == 1 else SpotState.OCCUPIED)
        color = "rgb(255, 0, 0)" if state == 1 else "rgb(0, 255, 0)"
        spot.setStyleSheet(f"background-color: {color}")

    def publish(self, data):
        # Publish a message
        CLIENT.publish("design3_bcg009", data)

    def sendText(self):
        # Send text using the publisher
        data = self.PAText.toPlainText()
        self.publish(data)

    def warnOn(self):
        # Set warning light on and red
        self.warningLight.setStyleSheet("background-color: rgb(255, 0, 0)")
        data = 1  # 1 = ALARM ON
        self.publish(data)

    def warnOff(self):
        # Set warning light off and grey
        self.warningLight.setStyleSheet("background-color: rgb(143, 143, 143)")
        data = 0  # 0 = ALARM OFF
        self.publish(data)

    def exit_func(self):
        # Exit the application
        sys.exit()

if __name__ == "__main__":
    # Run the application
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())