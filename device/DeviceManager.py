import requests
import json
import time
from MyMQTT import * 
import threading


class Device:
    def __init__(self, catalog_file, device_key):
        self.config = json.load(open(catalog_file, 'r'))
        self.mqttinfo = self.config['MQTTInfo']
        self.broker = self.mqttinfo["broker"]
        self.port = self.mqttinfo["port"]
        self.restaddr = self.config['RESTInfo']
        self.device = self.config[device_key]
        self.mqttid = self.device["mqtt_id"]
        self.status = self.device['reg_status']
        self.deviceid = self.device['deviceID']
        self.topic = self.device['publish']
        self.control_topic = self.device['subscribe']
        # print(f'the control topic is {self.control_topic}.')
        if self.control_topic == '':
            self.control_topic = None
            print(f'there is no control topic.')
            self.client = MyMQTT(self.mqttid, self.broker, self.port, None)
        else:
            print(f'the control topic is {self.control_topic}.')
            self.client = MyMQTT(self.mqttid, self.broker, self.port, self)
        self.name = self.mqttid.split('_')[1]
        self._message = {'client': self.mqttid,'n':self.name,'value':'', 'timestamp':'','unit':"status"}
        # self.client = MyMQTT(self.mqttid, self.broker, self.port, self)
        self.running = True
        self.thread = None
        
    def registerDevice(self):
        url = self.restaddr
        url = url + "device"
        print( f'The url is {url}.')
        data = {'ID': int(self.deviceid)}
        response = requests.post(url, json=data)
        resp_data = response.json()
        print(f'The response of the post is {resp_data}.')
        if self.status == True:
            print(f'The device is already registered.')
        else:
            if resp_data == True:
                self.device['reg_status'] = True
                self.status = self.device['reg_status']
                with open('device/config/device.json', 'w') as f:
                    json.dump(self.config, f) 
    
    def pingCatalog(self):
        while self.running:
            url = self.restaddr + "device"
            print(f'The url is {url}.')
            data = {'ID': int(self.deviceid)}
            print(f'The data is {data}.')
            response = requests.get(url, params=data)
            try:
                respdata = json.loads(response.json())
                status = respdata['status']
                if status == True:
                    self.status = True
                    print(f'The device reg status is updated.')
            except json.JSONDecodeError:
                print(f"Failed to decode JSON from response: {response.text}")
                continue 
            time.sleep(120)
            
    def startSim(self):
        self.client.start()
        if self.control_topic is not None:
            self.client.mySubscribe(self.control_topic)
            
    def stopSim(self):
        self.client.stop()
        
    def runfile(self):
        if not self.status:
            self.registerDevice()
        if self.status:
            print(f'The device is registered successfully.')
            time.sleep(2)
            self.device_thread = threading.Thread(target=self.device_behavior)
            self.ping_thread = threading.Thread(target=self.pingCatalog)
            self.device_thread.start()
            self.ping_thread.start()
        else:
            print(f'The device is not registered.')
    
    def stop(self):
        self.running = False
        self.stopSim()
        if hasattr(self, 'device_thread'):
            self.device_thread.join()
        if hasattr(self, 'ping_thread'):
            self.ping_thread.join()
            
    def device_behavior(self):
        raise NotImplementedError("This method should be implemented by subclasses")