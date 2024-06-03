from ControlManager import Control
import time
import json

class AirControl(Control):
    def __init__(self, catalog):
        super().__init__(catalog, 'Aircontrol')
        self.subtopic1 = self.controlinfo['subtopic1']
        self.subtopic2 = self.controlinfo['subtopic2']
        self.pubtopic = self.controlinfo['pubtopic']
        self.tempmsg = None
        self.humidmsg = None
        self.airsyb = 0
        
    def startSim(self):
        self.client.start()
        self.client.mySubscribe(self.subtopic1)
        self.client.mySubscribe(self.subtopic2)
        
    def notify(self, topic, payload):
        msg = json.loads(payload)
        msg_type = msg["n"]
        if msg_type == "temperature":
            self.tempmsg = msg
        elif msg_type == "humidity":
            self.humidmsg = msg
        else:
            print("Invalid message type")
            
    def control_behavior(self):
        self.startSim()
        try:
            if self.tempmsg is not None and self.humidmsg is not None:
                if self.tempmsg["value"] > 30 and self.humidmsg["value"] > 50:
                    if self.airsyb == 0:
                        operationmsg = self._message.copy()
                        operationmsg["value"] = 'on'
                        operationmsg["timestamp"] = time.time()
                        self.airsyb = 1
                        print("Turning on the air conditioner")
                        self.client.myPublish(self.pubtopic, operationmsg)
                        print(f"Published message: {operationmsg}")
                if self.tempmsg["value"] < 30 and self.humidmsg["value"] < 50:
                    if self.airsyb == 1:
                        operationmsg = self._message.copy()
                        operationmsg["value"] = 'off'
                        operationmsg["timestamp"] = time.time()
                        self.airsyb = 0
                        print("Turning off the air conditioner")
                        self.client.myPublish(self.pubtopic, operationmsg)
                        print(f"Published message: {operationmsg}")
                self.tempmsg = None
                self.humidmsg = None
            time.sleep(10)
        finally:
            self.stopSim()
            
if __name__ == '__main__':
    aircont = AirControl('control/config/control.json')
    aircont.runfile()
    while True:
        if input()=='q':
            aircont.stop()
            print("The service has been stopped.")
            break   