from DeviceManager import Device
import json
import time
# from led_main import LED

class Light(Device):
    def __init__(self, catalog_file):
        super().__init__(catalog_file, 'Device_light')
        self.light_actsyb = 0
        self.lightsyb = None
        # self.led = LED(36)
        
    def notify(self, topic, payload):
        msg = json.loads(payload)
        msg_type = msg['n']
        if msg_type == 'timecon' or msg_type =='light':
            if msg['value'] == 'on' :
                self.light_actsyb = 1
            elif msg['value'] == 'off':
                self.light_actsyb = 0
            print(f"The message is {msg}")
        else:
            print("Invalid message type")
    
    def device_behavior(self):
        try:
            self.startSim()
            while True:
                if self.light_actsyb == 1:
                    if self.lightsyb != self.light_actsyb:
                        message = self._message
                        message['timestamp'] = time.time()
                        message['value'] = 1
                        # self.led.openled(10)
                        self.client.myPublish(self.topic, message)
                        print(f"Published message: {message}")
                        self.lightsyb = self.light_actsyb
                elif self.light_actsyb == 0:
                    if self.lightsyb != self.light_actsyb:
                        message = self._message
                        message['timestamp'] = time.time()
                        message['value'] = 0
                        # self.led.closeled(10)
                        self.client.myPublish(self.topic, message)
                        print(f"Published message: {message}")
                        self.lightsyb = self.light_actsyb
        finally:
            self.stopSim()
            # self.led.clean()
            
if __name__ == "__main__":
    light = Light('config/device.json')
    light.runfile()
    while True:
        if input()=='q':
            light.stop()
            print("The service has been stopped.")
            break      