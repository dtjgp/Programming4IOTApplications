from DeviceManager import Device
import time
# import random
from dht_main import DHT11

class Humi(Device):
    def __init__(self, catalog_file):
        super().__init__(catalog_file, 'Device_humi')
        self.dht = DHT11()
        
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
        # message['value'] = random.randint(40,60)
        humid, _ = self.dht.DHT11_read()
        humid = round(humid, 2)
        message['value'] = humid
        self.client.myPublish(self.topic,message)
        print(f"published Message: \n {message}")
        
if __name__ == '__main__':
    humi = Humi('device/config/device.json')
    humi.runfile()
    while True:
        if input()=='q':
            humi.stop()
            print("The service has been stopped.")
            break