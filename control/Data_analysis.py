from ControlManager import Control
import time
import json

class DataAnalysis(Control):
    def __init__(self, catalog):
        super().__init__(catalog, 'Datacontrol')
        self.subtopic1 = self.controlinfo['subtopic1']
        self.subtopic2 = self.controlinfo['subtopic2']
        self.pubtopic1 = self.controlinfo['pubtopic1']
        self.pubtopic2 = self.controlinfo['pubtopic2']
        self.toilet_daythreshold = self.controlinfo['day_threshold']
        self.toilet_weekthreshold = self.controlinfo['week_threshold']
        self._message1 = {'client': self.clientID, 'n': 'toilet', 'value': '', 'timestamp': '', 'unit': 'status'}
        self._message2 = {'client': self.clientID, 'n': 'door', 'value': '', 'timestamp': '', 'unit': 'status'}
        self.toilet_day = 0
        self.toilet_week = 0
        self.door_day = 0
        
    def startSim(self):
        self.client.start()
        self.client.mySubscribe(self.subtopic1)
        self.client.mySubscribe(self.subtopic2)
        
    def notify(self, topic, payload):
        msg = json.loads(payload)
        msg_type = msg["n"]
        if msg_type == "toilet":
            self.toilet_day += msg["value"]
            self.toilet_week += msg["value"]
        elif msg_type == "door":
            self.door_day += msg["value"]
            
    def control_behavior(self):
        self.startSim()
        try:
            curhour = time.localtime().tm_hour
            if curhour == 0:
                self.toilet_day = 0
                message = self._message2.copy()
                message["value"] = self.door_day
                message["timestamp"] = time.time()
                self.client.myPublish(self.pubtopic2, message)
                self.door_day = 0
            if curhour == 0 and time.localtime().tm_wday == 0:
                self.toilet_week = 0
            if self.toilet_day > self.toilet_daythreshold:
                message = self._message1.copy()
                message["value"] = self.toilet_day 
                message["timestamp"] = time.time()
                self.client.myPublish(self.pubtopic1, message)
                print(f"Published message: {message}")
            if self.toilet_week > self.toilet_weekthreshold:
                message = self._message1.copy()
                message["value"] = self.toilet_week
                message["timestamp"] = time.time()
                self.client.myPublish(self.pubtopic1, message)
                print(f"Published message: {message}")
            time.sleep(3600)
        finally:
            self.stopSim()
            
if __name__ == '__main__':
    toiletinfo = DataAnalysis('control/config/control.json')
    toiletinfo.runfile()    
    while True:
        if input()=='q':
            toiletinfo.stop()
            print("The service has been stopped.")
            break
        