from DeviceManager import Device
import time
from motion_main import Motion
import requests
import random

class Door(Device):
    def __init__(self, catalog_file):
        super().__init__(catalog_file, 'Device_door')
        self.teleaddr = self.device['tele_addr']
        self.doorstate = None
        self.door_status = 0
        self.motion = Motion()
        
    def device_behavior(self):
        self.startSim()
        try:
            while self.running:
                self.publish()
                time.sleep(10)
        finally:
            self.stopSim()
            self.motion.clean()
            
    def publish(self):
        message = self._message
        message['timestamp'] = time.time()
        rand = random.random()
        # if rand > 0.3:
        #     self.doorstate = 1
        # else:
        #     self.doorstate = 0
        # message['value'] = int(self.doorstate)
        # if self.door_status != self.doorstate:
        #     self.client.myPublish(self.topic, message)
        #     print(f'The message is {message}.')
        #     self.door_status = self.doorstate
        self.doorstate = self.motion.readStat()
        if self.doorstate is not None:
            print(f"the current state is: {self.doorstate}")
            message['value'] = int(self.doorstate)
            if self.door_status != self.doorstate:
                self.client.myPublish(self.topic, message)
                print(f'The message is {message}.')
                self.door_status = self.doorstate
                url = self.teleaddr
                if self.door_status == 1:
                    data = {'alert': "your cat is at the door", 'action': "do something"}
                    response = requests.post(url, json=data)
                    resp_status = response.json()['status']
                    print(f'The response of the post is {resp_status}.')
                elif self.door_status ==0:
                    data = {'alert': "your cat get back to the room", 'action': "relax"}
                    response = requests.post(url, json=data)
                    resp_status = response.json()['status']
                    print(f'The response of the post is {resp_status}.')
                    
if __name__ == "__main__":
    door = Door('config/device.json')
    door.runfile()
    while True:
        if input()=='q':
            door.stop()
            print("The service has been stopped.")
            break       