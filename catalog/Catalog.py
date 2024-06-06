'''
    The Catalog works as service and device registry system for all the actors in the system. 
    It provides information about end-points (i.e. REST Web Services and MQTT topics) of all the devices, 
    resources and services in the platform. 
    It also provides configuration settings for applications and control strategies (e.g. list of sensors and actuators). 
    Each actor, during its start-up, must retrieve such information from the Catalog exploiting its REST Web Services. 
'''
# from ThingSpeakClass import ThingSpeak
# from service import CataService
import json
import requests
import cherrypy
import threading
import time 


class Catalog:
    exposed = True 

    def __init__(self, catalog_file):
        self.config = json.load(open(catalog_file, 'r'))
        self.fetch_timer = None
        self.device_list, self.service_list, self.control_list = self.get_ids()
        self.reged_device_list, self.reged_service_list, self.reged_control_list = [], [], [] 
        self.host = self.config["RESTInfo"]["host"]
        self.port = self.config["RESTInfo"]["port"]
        self.status = None
        self.respond = None
        
    def get_ids(self):
        device_list = []
        service_list = []
        control_list = []
        for device in self.config["DeviceList"]:
            device_list.append(device["id"])
        print("Device list:", device_list)
        for service in self.config["ServiceList"]:
            service_list.append(service["id"])
        print("Service list:", service_list)
        for control in self.config["ControlList"]:
            control_list.append(control["id"])
        print("Control list:", control_list)
        return device_list, service_list, control_list

    def Service(self):
        cherrypy.config.update({
            'server.socket_host': self.host,
            'server.socket_port': self.port
        })
        cherrypy.quickstart(self, '/', {
            '/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                'tools.sessions.on': True,
            }
        })
        
    @cherrypy.tools.json_out()
    def GET(self, *uri, **params):
        # response=json.load(params)
        if len(uri)==0: #An error will be raised in case there is no uri 
           raise cherrypy.HTTPError(status=400, message='UNABLE TO MANAGE THIS URL')
        elif uri[0]=='device':
            device_id = params.get('ID', None)
            if device_id is not None:
                # transform the device_id to int
                device_id = int(device_id)
                if device_id in self.device_list:
                    timestamp = time.time()
                    output = {"device":device_id, "status":True, "timestamp":timestamp}
            else:
                raise cherrypy.HTTPError(400, 'DEVICE NOT REGISTERED')
        elif uri[0]=='service':
            service_id = params.get('ID', None)
            if service_id is not None:
                # transform the service_id to int
                service_id = int(service_id)
                if service_id in self.service_list:
                    timestamp = time.time()
                    output = {"service":service_id, "status":True, "timestamp":timestamp}
            else:
                raise cherrypy.HTTPError(400, 'SERVICE NOT REGISTERED')
        elif uri[0]=='control':
            control_id = params.get('ID', None)
            if control_id is not None:
                # transform the control_id to int
                control_id = int(control_id)
                if control_id in self.control_list:
                    timestamp = time.time()
                    output = {"control":control_id, "status":True, "timestamp":timestamp}
            else:
                raise cherrypy.HTTPError(400, 'CONTROL NOT REGISTERED')
        return json.dumps(output)
    
    def POST(self, *uri, **params):
        body = cherrypy.request.body.read()
        json_body = json.loads(body.decode('utf-8'))
        if uri[0]=='device':
            if json_body['ID'] not in self.device_list:
                raise cherrypy.HTTPError(status=400, message='DEVICE NOT REGISTERED')
            if json_body['ID'] not in self.reged_device_list:
                self.reged_device_list.append(json_body['ID'])
                # find out the id in the json file
                for device in self.config["DeviceList"]:
                    if device["id"] == json_body['ID']:
                        device["register_status"] = True
                with open('catalog/config/catalog.json', 'w') as f:
                    json.dump(self.config, f)
            return json.dumps(True)
        elif uri[0]=='service':
            if json_body['ID'] not in self.service_list:
                raise cherrypy.HTTPError(status=400, message='SERVICE NOT REGISTERED')
            if json_body['ID'] not in self.reged_service_list:
                self.reged_service_list.append(json_body['ID'])
                for service in self.config["ServiceList"]:
                    if service["id"] == json_body['ID']:
                        service["register_status"] = True
                with open('catalog/config/catalog.json', 'w') as f:
                    json.dump(self.config, f)
            return json.dumps(True)
        elif uri[0]=='control':
            if json_body['ID'] not in self.control_list:
                raise cherrypy.HTTPError(status=400, message='DEVICE NOT REGISTERED')
            if json_body['ID'] not in self.reged_control_list:
                self.reged_control_list.append(json_body['ID'])
                for control in self.config["ControlList"]:
                   if control["id"] == json_body['ID']:
                       control["register_status"] = True
                with open('catalog/config/catalog.json', 'w') as f:
                    json.dump(self.config, f)
            return json.dumps(True)
        else:
            raise cherrypy.HTTPError(status=400, message='INVALID URI')
        
    def startservice(self):
        service_thread = threading.Thread(target=self.Service)
        service_thread.start()

    def stop(self):
        cherrypy.engine.stop()
        cherrypy.engine.exit()
        print("Service has been stopped.")

if __name__ == '__main__':
    catalog = Catalog('config/catalog.json')
    catalog.startservice()
    while True:
        if input("stop running [q]:") == 'q':
            break
    catalog.stop()
    
