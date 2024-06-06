import requests
import json
from MyMQTT import *
import time
import uuid
import threading
import cherrypy

class Thingspeak_Adaptor:
    exposed=True
    def __init__(self,catalog):
        self.config = json.load(open(catalog, 'r'))
        self.mqttinfo = self.config['MQTTInfo']
        self.mqttbroker = self.mqttinfo['broker']
        self.mqttport = self.mqttinfo['port']
        self.subtopiclist = self.mqttinfo['subtopiclist']
        self.restinfo = self.config['RESTInfo']
        self.cataaddr = self.restinfo['CataAddr']
        self.adahost = self.restinfo['AdaptorAddr']
        self.adaport = self.restinfo['AdaptorPort']
        self.tsinfo = self.config['ThingSpeakInfo']
        self.tsurl = self.tsinfo['ThingspeakURL']
        self.tswapi = self.tsinfo['ChannelWriteAPIkey']
        self.tsrapi = self.tsinfo['ChannelReadAPIKey']
        self.serviceinfo = self.config['ServiceInfo']
        self.servicename = self.serviceinfo['name']
        self.serviceid = self.serviceinfo['ID']
        self.status = self.serviceinfo['reg_status']
        self.client = MyMQTT(str(uuid.uuid1()), self.mqttbroker, self.mqttport, self)
        self.running = True
        self.thread = None

    def regservice(self):
        url = self.cataaddr
        url = url + "service"
        print( f'The url is {url}.')
        data = {'ID': int(self.serviceid)}
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                resp_data = response.json()
                print(f'The response of the post is {resp_data}.')
                resp_status = resp_data['status']
                if resp_status == True:
                    self.serviceinfo['reg_status'] = True
                    self.status = self.serviceinfo['reg_status']
                    with open('adaptor/config/adaptor.json', 'w') as f:
                        json.dump(self.config, f)
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")   
        if self.status:
            print(f'The service is registered.')
        else:
            print(f'The service is not registered.')
    
    def updatestatus(self):
        while self.running:
            url = self.cataaddr
            print(f'The url is {url}.')
            data = {'service': int(self.serviceid)}
            print(f'The data is {data}.')
            response = requests.put(url, json=data)
            try:
                if response.status_code == 200:
                    respdata = response.json()
                    print(f'The status is {respdata}.')
                    resp_status = respdata['status'] 
                    if resp_status == 'alive':
                        print(f'The service reg status is alive and updated.')
                        self.status = True
                    else:
                        self.status = False
                        print(f'The service reg status is not alive.')
            except json.JSONDecodeError:
                print(f"Failed to decode JSON from response: {response.text}")
            time.sleep(120)
                    
    def pingCatalog(self):
        while self.running:
            url = self.cataaddr + "service"
            print(f'The url is {url}.')
            data = {'ID': int(self.serviceid)}
            print(f'The data is {data}.')
            response = requests.get(url, params=data)
            try:
                respdata = json.loads(response.json())
                status = respdata['status']
                if status == True:
                    self.status = True
                    print(f'The servcice reg status is True and it is online.')
                else:
                    self.status = False
                    print(f'The control reg status is False and it is offline.')
            except json.JSONDecodeError:
                print(f"Failed to decode JSON from response: {response.text}")
                continue 
            time.sleep(200)
    
    def startSim(self): 
        self.client.start()
        for topic in self.subtopiclist:
            # print(f"Subscribing to topic: {topic}")
            self.client.mySubscribe(topic)
         
    def stopSim(self):
        self.client.stop()
    
    def notify(self,topic,payload):
        message_decoded=json.loads(payload)
        print(f'Received message from {topic} with payload {message_decoded}')
        value=message_decoded["value"]
        message={}
        message["value"]=value
        decide_measurement=message_decoded["n"]
        error=False
        if decide_measurement=="temperature":
            print("\n \n Temperature Message")
            message["field_number"]=1
        elif decide_measurement=="humidity":
            print("\n \n Humidity Message")
            message["field_number"]=2
        elif decide_measurement=="toilet":
            print("\n \n Toilet Message")
            message["field_number"]=3
        elif decide_measurement=="door":
            print("\n \n Door Message")
            message["field_number"]=4
        elif decide_measurement=="kitchen":
            print("\n \n Kitchen Message")
            message["field_number"]=5
        elif decide_measurement=="aircon":
            print("\n \n Aircon Message")
            message["field_number"]=6
        elif decide_measurement=="light":
            print("\n \n Light Message")
            message["field_number"]=7
        elif decide_measurement=="attract":
            print("\n \n Attract Message")
            message["field_number"]=8
        else: 
            error=True
        if error:
            print("Error")
        else:
            print(f'The message is: {message}')
            self.uploadThingspeak(field_number=message["field_number"],field_value=message["value"])
    
    def uploadThingspeak(self,field_number,field_value):
        urlToSend=f'{self.tsurl}{self.tswapi}&field{field_number}={field_value}'
        r=requests.get(urlToSend)
        # print(r.text)
        
    def runservice(self):
        try:
            self.startSim()
            while self.running:
                # time.sleep(1)
                pass
        finally:
            self.stopSim()
        
    def startweb(self):
        self.web_thread = threading.Thread(target=self.webservice)
        self.web_thread.start()
            
    def webservice(self):
        cherrypy.config.update(
            {
            'server.socket_host': self.adahost,  
            'server.socket_port': self.adaport,             
            }
        )
        cherrypy.quickstart(self,'/',config={'/':{
            'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on':True,
            }
        })
        
    @cherrypy.tools.json_out()
    def GET(self, *uri, **params):
        print(uri)
        if uri[0]=='data':
            readurl = f"https://api.thingspeak.com/channels/2516012/feeds.json?results=1"
            r=requests.get(readurl)
            feed = r.json()["feeds"]
        return feed
    
    def runfile(self):
        if not self.status:
            self.regservice()
        if self.status:
            print(f'The control logic is registered successfully.')
            time.sleep(2)
            self.adaptor_thread = threading.Thread(target=self.runservice) 
            self.ping_thread = threading.Thread(target=self.pingCatalog)
            self.status_thread = threading.Thread(target=self.updatestatus)
            self.adaptor_thread.start()
            self.ping_thread.start()
            self.status_thread.start()
            self.startweb()  # Start the web service thread here
        else:
            print(f'The control logic is not registered.')
            
    def stop(self):
        self.running = False
        if self.ping_thread:
            self.ping_thread.join()
        if self.adaptor_thread:
            self.adaptor_thread.join()
        if self.status_thread:
            self.status_thread.join()
        if self.web_thread:
            cherrypy.engine.exit()  # Ensure CherryPy server stops
            self.web_thread.join()
 
if __name__ == "__main__":
    ts_adaptor=Thingspeak_Adaptor('config/adaptor.json')
    ts_adaptor.runfile()
    while True:
        if input()=='q':
            ts_adaptor.stop()
            print("The service has been stopped.")
            break 
    
    
    



        

