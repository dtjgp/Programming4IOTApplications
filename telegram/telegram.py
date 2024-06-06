import json
import requests
import time
import cherrypy
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup
from MyMQTT import *
import threading

class Tele:
    exposed=True
    def __init__(self,catalog):
        self.config = json.load(open(catalog, 'r'))
        self.mqttinfo = self.config['MQTTInfo']
        self.broker = self.mqttinfo['broker']
        self.port = self.mqttinfo['port']
        self.mqttid = self.mqttinfo['mqttid']
        self.subtopic1 = self.mqttinfo['subtopic1']
        self.subtopic2 = self.mqttinfo['subtopic2']
        self.subtopic3 = self.mqttinfo['subtopic3']
        self.pubtopic1 = self.mqttinfo['pubtopic1']
        self.pubtopic2 = self.mqttinfo['pubtopic2']
        self.pubtopic3 = self.mqttinfo['pubtopic3']
        self.pubtopic4 = self.mqttinfo['pubtopic4']
        self.pubtopic5 = self.mqttinfo['pubtopic5']
        self.restinfo = self.config['RESTInfo']
        self.cataaddr = self.restinfo['CataAddr']
        self.host = self.restinfo['host']
        self.teleport = self.restinfo['TelePort']
        self.adaport = self.restinfo['AdaptorPort']
        self.tokenBot = self.config["telegramToken"]
        self.serviceinfo = self.config['ServiceInfo']
        self.servicename = self.serviceinfo['name']
        self.serviceid = self.serviceinfo['ID']
        self.status = self.serviceinfo['reg_status']
        self.chatIDs=[]
        self.running = True
        self.thread = None
        self.client = MyMQTT(self.mqttid, self.broker, self.port, self)
        self.bot = telepot.Bot(self.tokenBot)
        self.__message={'client': self.mqttid,'n':'','value':'', 'timestamp':'','unit':"status"}
        self.querydata = {"Time":None,"temperature":None,"humidity":None, "toilet":None, "door":None, "kitchen":None, "aircon":None, "light":None, "Attract":None} 
        self.chat_states = {}
        MessageLoop(self.bot, {'chat': self.on_chat_message,
                               'callback_query': self.on_callback_query}).run_as_thread()

    def regservice(self):
        url = self.cataaddr
        url = url + "service"
        print( f'The url is {url}.')
        service_id = self.serviceid
        data = {'ID': int(service_id)}
        response = requests.post(url, json=data)
        resp_data = response.json()
        print(f'The response of the post is {resp_data}.')
        if self.status == True:
            print(f'The device is already registered.')
        else:
            if resp_data == True:
                self.serviceinfo['reg_status'] = True
                self.status = self.serviceinfo['reg_status']
                with open('telegram/config/telegram.json', 'w') as f:
                    json.dump(self.config, f)
                    
    def pingCatalog(self):
        while self.running:
            url = self.cataaddr + "service"
            print(f'The url is {url}.')
            service_id = self.serviceid
            data = {'ID': int(service_id)}
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
        self.client.mySubscribe(self.subtopic1)
        self.client.mySubscribe(self.subtopic2)
    
    def teleservice(self):
        cherrypy.config.update(
            {
            'server.socket_host': self.host, 
            'server.socket_port': self.teleport,             
            }
        )
        cherrypy.quickstart(self,'/',config={'/':{
            'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on':True,
            }
        })
        
    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        self.chatIDs.append(chat_ID)
        # print(f'Chat IDs: {self.chatIDs}')
        message = msg['text']
        if chat_ID in self.chat_states:
            if self.chat_states[chat_ID] == 'adding_time':
                input_time = message
                # check if the input is a valid number
                try:
                    input_time = int(input_time)
                    payload = self.__message.copy()
                    payload['n'] = "timeadd"
                    payload['value'] = input_time
                    payload['timestamp'] = time.time()
                    self.client.myPublish(self.pubtopic4, payload)
                    self.bot.sendMessage(chat_ID, text=f'The time you entered is {input_time}')
                    del self.chat_states[chat_ID]
                    return
                except ValueError:
                    self.bot.sendMessage(chat_ID, text='Please enter a valid number')
                    return
            elif self.chat_states[chat_ID] == 'deleting_time':
                input_time = message
                # check if the input is a valid number
                try:
                    input_time = int(input_time)
                    payload = self.__message.copy()
                    payload['n'] = "timedel"
                    payload['value'] = input_time
                    payload['timestamp'] = time.time()
                    self.client.myPublish(self.pubtopic5, payload)
                    self.bot.sendMessage(chat_ID, text=f'The time you entered is {input_time}')
                    del self.chat_states[chat_ID]
                    return
                except ValueError:
                    self.bot.sendMessage(chat_ID, text='Please enter a valid number')
                    return
        if message=='/AttOn':
            payload = self.__message.copy()
            payload['n'] = "attractcon"
            payload['value'] = "on"
            payload['timestamp'] = time.time()
            # print(f'The payload is {payload}')
            self.client.myPublish(self.pubtopic2, payload)
            self.bot.sendMessage(chat_ID, text="Attraction switched on")
        elif message=='/AirOn':
            payload = self.__message.copy()
            payload['n'] = "aircon"
            payload['value'] = "on"
            payload['timestamp'] = time.time()
            self.client.myPublish(self.pubtopic1, payload)
            self.bot.sendMessage(chat_ID, text="Aircon switched on")
        elif message=='/AirOff':
            payload = self.__message.copy()
            payload['n'] = "aircon"
            payload['value'] = "off"
            payload['timestamp'] = time.time()
            self.client.myPublish(self.pubtopic1, payload)
            self.bot.sendMessage(chat_ID, text="Attraction switched off")
        elif message=="/getdata":
            # data = self.getdata()[0]
            # query = self.querydata.copy()
            # query["Time"] = data["created_at"]
            # query["temperature"] = data["field1"]
            # query["humidity"] = data["field2"]
            # query["toilet"] = data["field3"]
            # query["door"] = data["field4"]
            # query["kitchen"] = data["field5"]
            # query["aircon"] = data["field6"]
            # query["light"] = data["field7"]
            # query["Attract"] = data["field8"]
            # qtime = query["Time"]
            # qtemp = query["temperature"]
            # qhum = query["humidity"]
            # qtoilet = query["toilet"]
            # qdoor = query["door"]
            # qkitchen = query["kitchen"]
            # qaircon = query["aircon"]
            # qlight = query["light"]
            # qattract = query["Attract"]
            # query = f"Time: {qtime}\nTemperature: {qtemp}\nHumidity: {qhum}\nToilet: {qtoilet}\nDoor: {qdoor}\nKitchen: {qkitchen}\nAircon: {qaircon}\nLight: {qlight}\nAttract: {qattract}"
            # self.bot.sendMessage(chat_ID, text=query)
            url = 'http://192.168.5.11:1880/ui'
            self.bot.sendMessage(chat_ID, text=f'please click here to check the data: {url}')
        elif message == "/LightOn":
            payload = self.__message.copy()
            payload['n'] = "light"
            payload['value'] = "on"
            payload['timestamp'] = time.time()
            print(f'The payload is {payload}')
            self.client.myPublish(self.pubtopic3, payload)
            self.bot.sendMessage(chat_ID, text="Attraction switched on")
        elif message == "/LightOff":
            payload = self.__message.copy()
            payload['n'] = "light"
            payload['value'] = "off"
            payload['timestamp'] = time.time()
            print(f'The payload is {payload}')
            self.client.myPublish(self.pubtopic3, payload)
            self.bot.sendMessage(chat_ID, text="Attraction switched off")
        # set a kitchen time modification, the user will be asked to enter a time，and the time user entered will be added to the kitchen time list
        elif message == "/AddKitTime":
            self.chat_states[chat_ID] = 'adding_time'
            self.bot.sendMessage(chat_ID, text="Please enter a time to add to the kitchen time list")
        elif message == "/DelKitTime":
            self.chat_states[chat_ID] = 'deleting_time'
            self.bot.sendMessage(chat_ID, text="Please enter a time to delete from the kitchen time list")
        elif message=="/start":
            self.bot.sendMessage(chat_ID, text="Welcome")
        else:
            self.bot.sendMessage(chat_ID, text="Command not supported")
    
    def notify(self,topic,message):
        print(message)
        msg=json.loads(message)
        self.tempthreshold=30
        if msg["n"]=="temperature":
            if msg["value"]>self.tempthreshold:
                tosend=f"Temperature is reaching {msg['value']}, do you want to turn on the aircon?"
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Yes', callback_data='yes'),
                    InlineKeyboardButton(text='No', callback_data='no')]
                ])
                for chat_ID in self.chatIDs:
                    self.bot.sendMessage(chat_ID, text=tosend, reply_markup=keyboard)
        elif msg["n"]=="toiletcon":
            tosend="ATTENTION!!! Your cat has used unnormal times. You should be care of it."
            for chat_ID in self.chatIDs:
                self.bot.sendMessage(chat_ID, text=tosend)
        elif msg["n"]=="doorcon":
            tosend=f"Your cat try {msg['value']} times to go outside."
            for chat_ID in self.chatIDs:
                self.bot.sendMessage(chat_ID, text=tosend)
                    
    def on_callback_query(self,msg):
        query_ID , chat_ID , query_data = telepot.glance(msg,flavor='callback_query')
        payload = self.__message.copy()
        payload['n'] = "aircon"
        payload['timestamp'] = time.time()
        if query_data == 'yes':
            payload['value'] = "on"
            self.client.myPublish(self.pubtopic1, payload)
            print('aircon switched on message sent')
            self.bot.sendMessage(chat_ID, text=f"Aircon switched {query_data}")
        elif query_data == 'no':
            pass
            
    def POST(self,*uri):
        tosend=''
        output={"status":"not-sent","message":tosend}
        if len(uri)!=0:
            if uri[0]=='door':
                body=cherrypy.request.body.read()
                jsonBody=json.loads(body)
                alert=jsonBody["alert"]
                action=jsonBody["action"]
                tosend=f"ATTENTION!!!\n{alert}, you should {action}"
                output={"status":"sent","message":tosend}
                for chat_ID in self.chatIDs:
                    self.bot.sendMessage(chat_ID, text=tosend)
        return json.dumps(output)
    
    def getdata(self):
        url = f"http://{self.host}:{self.adaport}/data"
        print(f'The url is {url}.')
        response = requests.get(url)
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            print('Warning: Could not decode JSON from response')
            data = None
        return data
        
    def runfile(self):
        if not self.status:
            self.regservice()
        if self.status:
            print(f'The service is registered successfully.')
            time.sleep(2)
            self.startSim()
            self.tele_thread = threading.Thread(target=self.teleservice)
            self.ping_thread = threading.Thread(target=self.pingCatalog)
            self.tele_thread.start()
            self.ping_thread.start()
        else:
            print(f'The service is not registered.')
            
    def stop(self):
        self.running = False
        if self.ping_thread:
            self.ping_thread.join()
        if self.tele_thread:
            self.tele_thread.join()
    

if __name__ == "__main__":
    tele=Tele('config/telegram.json')
    tele.runfile()
    while True:
        if input("stop running [q]:") == 'q':
            tele.stop()
            break
    