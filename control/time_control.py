from ControlManager import Control
import time
import json

class TimeControl(Control):
    def __init__(self, catalog):
        super().__init__(catalog, 'Timecontrol')
        self.subtopic1 = self.controlinfo['subtopic1']
        self.subtopic2 = self.controlinfo['subtopic2']
        self.pubtopic1 = self.controlinfo['pubtopic1']
        self.pubtopic2 = self.controlinfo['pubtopic2']
        self.kitchentimes = self.controlinfo["kitchen_timelist"]
        self.openlighttimes = self.controlinfo["open_light"]
        self.closelighttimes = self.controlinfo["close_light"]
        print(f'pubtopic1: {self.pubtopic1}')
        print(f'pubtopic2: {self.pubtopic2}')
        print(f"Kitchen times: {self.kitchentimes}")
        print(f"Open light times: {self.openlighttimes}")
        print(f"Close light times: {self.closelighttimes}")
        self.timeadd = 0
        self.timedel = 0
        
    def update_config_file(self):
        try:
            with open('config/control.json', 'w') as f:
                json.dump(self.config, f)
            print("Configuration successfully updated to file.")
        except Exception as e:
            print(f"Failed to update configuration file: {e}")

    def startSim(self):
        self.client.start()
        self.client.mySubscribe(self.subtopic1)
        self.client.mySubscribe(self.subtopic2)
    
    def notify(self, topic, payload):
        msg = json.loads(payload)
        msg_type = msg["n"]
        if msg_type == "timeadd":
            self.timeadd = msg["value"]
            if self.timeadd not in self.kitchentimes:
                self.kitchentimes.append(self.timeadd)
                self.kitchentimes.sort()
                # save the updated list to the json file
                self.controlinfo["kitchen_timelist"] = self.kitchentimes
                self.update_config_file()
                self.kitchentimes = self.controlinfo["kitchen_timelist"]
                self.timeadd = 0
        elif msg_type == "timedel":
            self.timedel = msg["value"]
            if self.timedel in self.kitchentimes:
                self.kitchentimes.remove(self.timedel)
                self.kitchentimes.sort()
                # save the updated list to the json file
                self.controlinfo["kitchen_timelist"] = self.kitchentimes
                self.update_config_file()
                self.kitchentimes = self.controlinfo["kitchen_timelist"]
                self.timedel = 0
        else:
            print("Invalid message type")
        
    def control_behavior(self):
        self.startSim()
        try:
            while self.running:
                curhour = time.localtime().tm_hour
                message = self._message.copy()  
                if curhour in self.kitchentimes:
                    message["value"] = 'on'
                    message["timestamp"] = time.time()
                    print("Turning on the food locker")
                    self.client.myPublish(self.pubtopic1, message)
                    print(f"Published message: {message}, to the pubtopic1: {self.pubtopic1}.")
                if curhour in self.openlighttimes:
                    message["value"] = 'on'
                    message["timestamp"] = time.time()
                    print("Turning on the light")
                    self.client.myPublish(self.pubtopic2, message)
                    print(f"Published message: {message}, to the pubtopic2: {self.pubtopic2}.")
                if curhour in self.closelighttimes:
                    message["value"] = 'off'
                    message["timestamp"] = time.time()
                    print("Turning off the light")
                    self.client.myPublish(self.pubtopic2, message)
                    print(f"Published message: {message}, to the pubtopic2: {self.pubtopic2}.")
                time.sleep(1)
        finally:
            self.stopSim()
            
if __name__ == "__main__":
    timecon = TimeControl('config/control.json')
    timecon.runfile()
    while True:
        if input()=='q':
            timecon.stop()
            print("The service has been stopped.")
            break   