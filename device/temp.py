from DeviceManager import Device
import time
import random
#from dht_main import DHT11

class Temp(Device):
    def __init__(self, catalog_file):
        super().__init__(catalog_file, 'Device_temp')
        #self.dht = DHT11()
        
    def device_behavior(self):
        self.startSim()
        try:
            while self.running:
                self.publish()
                time.sleep(10)
        finally:
            self.stopSim()
            
    def publish(self):
        message=self._message
        message['timestamp']=time.time()
        message['value']=random.randint(20,35)
        #_, temp = self.dht.DHT11_read()
        #temp = round(temp, 2)
        #message['value'] = temp
        self.client.myPublish(self.topic,message)
        print(f"published Message: \n {message}")
        
if __name__ == '__main__':
    temp = Temp('config/device.json')
    temp.runfile()
    while True:
        if input()=='q':
            temp.stop()
            print("The service has been stopped.")
            break