from DeviceManager import Device
import json
import time
from led_main import LED

class Attract(Device):
    def __init__(self, catalog_file):
        super().__init__(catalog_file, 'Device_attract')
        self.attractsyb = 0
        self.led = LED(22)
    
    def notify(self, topic, payload):
        msg = json.loads(payload)
        msg_type = msg['n']
        if msg_type == 'attractcon':
            if msg['value'] == 'on':
                print("The Open message received!")
                self.attractsyb = 1
        else:
            print("Invalid message type")
            
    def device_behavior(self):
        try:
            self.startSim()
            while True:
                if self.attractsyb == 1:
                    self.led.openled(10)
                    print(f'The attractor is on.')
                    message = self._message
                    message['timestamp'] = time.time()
                    message['value'] = int(1)
                    self.client.myPublish(self.topic, message)
                    print(f"published Message: \n {message}")
                    # time.sleep(10)
                    self.led.closeled(5)
                    self.attractsyb = 0
                    message['value'] = int(0)
                    self.client.myPublish(self.topic, message)
                    print(f"published Message: \n {message}") 
                    print(f'The attractor is off.')
        finally:
            self.stopSim()
            self.led.clean()

if __name__ == '__main__': 
    attract = Attract('config/device.json')
    attract.runfile()
    while True:
        if input()=='q':
            attract.stop()
            print("The service has been stopped.")
            break   