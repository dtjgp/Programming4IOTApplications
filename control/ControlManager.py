from MyMQTT import * 
import json
import time
import threading
import requests

class Control:
    def __init__(self, catalog, control_key):
        self.config = json.load(open(catalog, 'r'))
        self.restaddr = self.config['RESTAddr']
        self.broker = self.config['MQTTInfo']['broker']
        self.port = self.config['MQTTInfo']['port']
        self.controlinfo = self.config[control_key]
        self.clientID = self.controlinfo['client']
        self.id = self.controlinfo['ID']
        self.status = self.controlinfo['reg_status']
        self.client = MyMQTT(self.clientID, self.broker, self.port, self)
        self._message = {'client': self.clientID, 'n': self.clientID, 'value': '', 'timestamp': '', 'unit': 'status'}
        self.running = True
        self.thread = None
        
    def registerControl(self):
        url = self.restaddr
        url = url + "control"
        print( f'The url is {url}.')
        data = {'ID': int(self.id)}
        response = requests.post(url, json=data)
        try:
            resp_data = response.json()
            print(f'The response of the post is {resp_data}.')
            if self.status == True:
                print(f'The device is already registered.')
            else:
                if resp_data == True:
                    self.controlinfo['reg_status'] = True
                    self.status = self.controlinfo['reg_status']
                    with open('control/config/control.json', 'w') as f:
                        json.dump(self.config, f) 
        except json.JSONDecodeError:
            print(f"Failed to decode JSON from response: {response.text}")
                    
    def pingCatalog(self):
        while self.running:
            url = self.restaddr + "control"
            print(f'The url is {url}.')
            data = {'ID': int(self.id)}
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
    
    def stopSim(self):
        self.client.stop()
        
    def runfile(self):
        if not self.status:
            self.registerControl()
        if self.status:
            print(f'The control logic is registered successfully.')
            time.sleep(2)
            self.control_thread = threading.Thread(target=self.control_behavior)
            self.ping_thread = threading.Thread(target=self.pingCatalog)
            self.control_thread.start()
            self.ping_thread.start()
        else:
            print(f'The control logic is not registered.')
            
    def stop(self):
        self.running = False
        self.stop_sim()
        if hasattr(self, 'control_thread'):
            self.control_thread.join()
        if hasattr(self, 'ping_thread'):
            self.ping_thread.join()

    def control_behavior(self):
        raise NotImplementedError("This method should be implemented by subclasses")