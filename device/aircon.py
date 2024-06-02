from DeviceManager import Device
import json
import time

class Aircon(Device):
    def __init__(self, catalog_file):
        super().__init__(catalog_file, 'Device_aircon')
        self.aircon_actsyb = False
        self.airconsyb = False
        
    def notify(self, topic, payload):
        print(f"Received message: {payload}")
        msg = json.loads(payload)
        msg_type = msg['n']
        if msg_type == 'aircon':
            if msg['value'] == 'on':
                self.aircon_actsyb = True
                print("Received message: ", msg)
            else:
                self.aircon_actsyb = False
        else:
            print("Invalid message type")
    
    def device_behavior(self):
        self.startSim()
        try:
            while self.running:
                if self.aircon_actsyb != self.airconsyb:
                    message = self._message
                    message['timestamp'] = time.time()
                    if self.airconsyb == True: 
                        message['value'] = int(1)             
                    elif self.airconsyb == False:
                        message['value'] = int(0)
                    self.client.myPublish(self.topic, message)
                    print(f"published Message: \n {message}")
                    self.aircon_actsyb = self.airconsyb
                time.sleep(10)
        finally:
            self.stopSim()

if __name__ == '__main__':
    aircon = Aircon('device/config/device.json')
    aircon.runfile()
    while True:
        if input()=='q':
            aircon.stop()
            print("The service has been stopped.")
            break   