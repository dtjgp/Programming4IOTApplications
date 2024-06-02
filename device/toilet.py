from DeviceManager import Device
import time
import random

class Toilet(Device):
    def __init__(self, catalog_file):
        super().__init__(catalog_file, 'Device_toilet')
        # self.topic = self.device['publish']
        self.toilet_status = 0
        self.toiletstate = None
    
    def device_behavior(self):
        self.startSim()
        try:
            while self.running:
                self.publish()
                time.sleep(10)
        finally:
            self.stopSim()
            
    def publish(self): 
        message = self._message
        message['timestamp'] = time.time()
        # message['value'] = random.randint(0, 1)
        rand = random.random()
        if rand > 0.8:
            message['value'] = 1
        else:
            message['value'] = 0
        message['value'] = int(message['value'])
        if self.toilet_status != self.toiletstate:
            self.client.myPublish(self.topic,message)
            print(f"published Message: \n {message}")
            self.toilet_status = self.toiletstate
            
if __name__ == "__main__":
    toilet = Toilet('device/config/device.json')
    toilet.runfile()
    while True:
        if input()=='q':
            toilet.stop()
            print("The service has been stopped.")
            break