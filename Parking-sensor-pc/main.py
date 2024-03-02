from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import smartParking_ui
import time as time
from PyQt5.QtWidgets import QMessageBox
import paho.mqtt.client as mqtt

#use a public brpker, declare objects/methods
mqttBroker = "broker.hivemq.com" # public broker
client = mqtt.Client("fake_temp1") # your name as client
client.connect(mqttBroker)

class MainWindow(QtWidgets.QMainWindow, smartParking_ui.Ui_MainWindow):
    # """UI Window class"""
    def __init__(self):
        """Initialize the window class"""
        super(MainWindow, self).__init__()
        self.setupUi(self)

        # subscribe
        client.loop_start()
        client.subscribe("design3_bcg009_sensor") # topic
        client.on_message = self.on_message # call a function


        self.sendButton.clicked.connect(self.sendText)
        self.onButton.clicked.connect(self.warnOn)
        self.offButton.clicked.connect(self.warnOff)
        # self.pushButton_2.clicked.connect(self.run_func)

    # Callback function
    def on_message(self, client, userdata, message):
        global b 
        b = message.payload.decode("utf-8")
        self.dataCheck(b)
        msg_list = b.split() 
        print("message recieved:", b)

    def dataCheck(self,data):
        dataList = data.split()
        # if len > 1 then its returning the lot values
        if(len(dataList) > 1):
            # lot 1
            if(dataList[0] == '1'):
                self.spotOne.setDigitCount(1)
                self.spotOne.display(0)
                self.spotOne.setStyleSheet("background-color: rgb(255, 0, 0)")
            if(dataList[0] == '0'):
                self.spotOne.setDigitCount(1)
                self.spotOne.display(1)
                self.spotOne.setStyleSheet("background-color: rgb(0, 255, 0)")

            # lot 2
            if(dataList[1] == '1'):
                self.spotTwo.setDigitCount(1)
                self.spotTwo.display(0)
                self.spotTwo.setStyleSheet("background-color: rgb(255, 0, 0)")
            if(dataList[1] == '0'):
                self.spotTwo.setDigitCount(1)
                self.spotTwo.display(1)
                self.spotTwo.setStyleSheet("background-color: rgb(0, 255, 0)")

            #lot 3
            if(dataList[2] == '1'):
                self.spotThree.setDigitCount(1)
                self.spotThree.display(0)
                self.spotThree.setStyleSheet("background-color: rgb(255, 0, 0)")
            if(dataList[2] == '0'):
                self.spotThree.setDigitCount(1)
                self.spotThree.display(1)
                self.spotThree.setStyleSheet("background-color: rgb(0, 255, 0)")

            #lot 4
            if(dataList[3] == '1'):
                self.spotFour.setDigitCount(1)
                self.spotFour.display(0)
                self.spotFour.setStyleSheet("background-color: rgb(255, 0, 0)")
            if(dataList[3] == '0'):
                self.spotFour.setDigitCount(1)
                self.spotFour.display(1)
                self.spotFour.setStyleSheet("background-color: rgb(0, 255, 0)")

            #lot 5
            if(dataList[4] == '1'):
                self.spotFive.setDigitCount(1)
                self.spotFive.display(0)
                self.spotFive.setStyleSheet("background-color: rgb(255, 0, 0)")
            if(dataList[4] == '0'):
                self.spotFive.setDigitCount(1)
                self.spotFive.display(1)
                self.spotFive.setStyleSheet("background-color: rgb(0, 255, 0)")


        #Otherwise its a normal string
        if(len(dataList) == 1):
            self.sensorText.setText(dataList[0])



    def publish(self,data):
        #publish message
        client.publish("design3_bcg009", data)

    def sendText(self):
        # send text using publisher
        data = self.PAText.toPlainText()
        self.publish(data)

    def warnOn(self):
        # set warning light on and red
        self.warningLight.setStyleSheet("background-color: rgb(255, 0, 0)")
        data = 1 # 1 = ALARM ON
        self.publish(data)

    def warnOff(self):
        #  set warning light off and grey
        self.warningLight.setStyleSheet("background-color: rgb(143, 143, 143)")
        data = 0 # 0 = ALARM OFF
        self.publish(data)



    def exit_func(self):
        exit()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
