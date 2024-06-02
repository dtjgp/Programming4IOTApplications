from DeviceManager import Device
import time
import json
from led_main import LED

class Kitchen(Device):
    def __init__(self, catalog_file):
        super().__init__(catalog_file, 'Device_kitchen')
        self.kit_actsyb = 0
        self.led = LED(36)
        
    def notify(self, topic, payload):
        msg = json.loads(payload)
        print(f"Received message: {msg}")
        if msg['n'] == 'timecon':
            if msg['value'] == 'on':
                self.kit_actsyb = 1
    
    def device_behavior(self):
        self.startSim()
        try:
            while self.running:
                if self.kit_actsyb == 1:
                    message = self._message
                    message['timestamp'] = time.time()
                    message['value'] = int(1)
                    self.led.openled(5)
                    self.client.myPublish(self.topic, message)
                    print(f"Published message: {message}")
                    # time.sleep(10)
                    self.led.closeled(5)
                    self.kit_actsyb = 0
                    self.client.myPublish(self.topic, message)
                    print(f"Published message: {message}")
                time.sleep(10)
        finally:
            self.stopSim()
            self.led.clean()

if __name__ == "__main__":
    kitchen = Kitchen('device/config/device.json')
    kitchen.runfile()
    while True:
        if input()=='q':
            kitchen.stop()
            print("The service has been stopped.")
            break   