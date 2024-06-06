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
        self.device_list, self.service_list, self.control_list, self.reged_device_list, self.reged_service_list, self.reged_control_list = self.get_ids()
        self.host = self.config["RESTInfo"]["host"]
        self.port = self.config["RESTInfo"]["port"]
        self.stop_event = threading.Event()

        
    def get_ids(self):
        device_list = []
        service_list = []
        control_list = []
        reged_device_list = {}
        reged_service_list = {}
        reged_control_list = {}
        for device in self.config["DeviceList"]:
            device_list.append(device["id"])
            reged_device_list[device["id"]] = 0
        print("Device list:", device_list)
        for service in self.config["ServiceList"]:
            service_list.append(service["id"])
            reged_service_list[service["id"]] = 0
        print("Service list:", service_list)
        for control in self.config["ControlList"]:
            control_list.append(control["id"])
            reged_control_list[control["id"]] = 0
        print("Control list:", control_list)
        return device_list, service_list, control_list, reged_device_list, reged_service_list, reged_control_list

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
    
    def check_alive(self):
        while not self.stop_event.is_set():
            self.stop_event.wait(300)
            print("Checking the alive status of devices, services and controls...")
            for device_id, alive_status in self.reged_device_list.items():
                if alive_status == 0:
                    # find the device in the config file and set the register_status to False
                    for device in self.config["DeviceList"]:
                        if device["id"] == device_id:
                            device["register_status"] = False
                    print(f'The device {device_id} is not alive')
            for service_id, alive_status in self.reged_service_list.items():
                if alive_status == 0:
                    for service in self.config["ServiceList"]:
                        if service["id"] == service_id:
                            service["register_status"] = False
                    print(f'The service {service_id} is not alive')
            for control_id, alive_status in self.reged_control_list.items():
                if alive_status == 0:
                    for control in self.config["ControlList"]:
                        if control["id"] == control_id:
                            control["register_status"] = False
                    print(f'The control {control_id} is not alive')
            with open('catalog/config/catalog.json', 'w') as f:
                json.dump(self.config, f)

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
                    for device in self.config["DeviceList"]:
                        if device["id"] == device_id:
                            device_stat = device["register_status"]
                    output = {"device":device_id, "status":device_stat, "timestamp":timestamp}
                    return json.dumps(output)
            else:
                raise cherrypy.HTTPError(400, 'DEVICE NOT REGISTERED')
        elif uri[0]=='service':
            service_id = params.get('ID', None)
            if service_id is not None:
                # transform the service_id to int
                service_id = int(service_id)
                if service_id in self.service_list:
                    timestamp = time.time()
                    for service in self.config["ServiceList"]:
                        if service["id"] == service_id:
                            service_stat = service["register_status"]
                    output = {"service":service_id, "status":service_stat, "timestamp":timestamp}
                    return json.dumps(output)
            else:
                raise cherrypy.HTTPError(400, 'SERVICE NOT REGISTERED')
        elif uri[0]=='control':
            control_id = params.get('ID', None)
            if control_id is not None:
                # transform the control_id to int
                control_id = int(control_id)
                if control_id in self.control_list:
                    timestamp = time.time()
                    for control in self.config["ControlList"]:
                        if control["id"] == control_id:
                            control_stat = control["register_status"]
                    output = {"control":control_id, "status":control_stat, "timestamp":timestamp}
                    return json.dumps(output)
            else:
                raise cherrypy.HTTPError(400, 'CONTROL NOT REGISTERED')
        else:
            raise cherrypy.HTTPError(400, 'INVALID URI')
    
    def PUT(self, *uri, **params):
        body = cherrypy.request.body.read()
        if len(body)>0:
            try:
                jsonBody=json.loads(body)
                for key in jsonBody.keys():
                    if key == 'device':
                        device_id = int(jsonBody[key])
                        if device_id in self.reged_device_list:
                            self.reged_device_list[device_id] += 1
                            response = {"device":device_id, "status":'alive'}
                            return json.dumps(response)
                        else:
                            raise cherrypy.HTTPError(400, 'DEVICE NOT REGISTERED')
                    elif key == 'service':
                        service_id = int(jsonBody[key])
                        if service_id in self.reged_service_list:
                            self.reged_service_list[service_id] += 1
                            response = {"service":service_id, "status":'alive'}
                            return json.dumps(response)
                        else:
                            raise cherrypy.HTTPError(400, 'SERVICE NOT REGISTERED')
                    elif key == 'control':
                        control_id = int(jsonBody[key])
                        if control_id in self.reged_control_list:
                            self.reged_control_list[control_id] += 1
                            response = {"control":control_id, "status":'alive'}
                            return json.dumps(response)
                        else:
                            raise cherrypy.HTTPError(400, 'CONTROL NOT REGISTERED')
                    else:
                        raise cherrypy.HTTPError(400, 'INVALID URI')
            except json.decoder.JSONDecodeError:
                raise cherrypy.HTTPError(400,"Bad Request. Body must be a valid JSON")
            except:
                raise cherrypy.HTTPError(500,"Internal Server Error")
        else:
            return json.dumps({"status":"No body in the request"})

    def POST(self, *uri, **params):
        body = cherrypy.request.body.read()
        json_body = json.loads(body.decode('utf-8'))
        if uri[0]=='device':
            if json_body['ID'] not in self.device_list:
                raise cherrypy.HTTPError(status=400, message='DEVICE NOT REGISTERED')
            if self.reged_device_list[json_body['ID']] == 0:
                self.reged_device_list[json_body['ID']] += 1
                for device in self.config["DeviceList"]:
                    if device["id"] == json_body['ID']:
                        device["register_status"] = True
                with open('catalog/config/catalog.json', 'w') as f:
                    json.dump(self.config, f)
                response = {"device":json_body['ID'], "status":True}
            else:
                response = {"device":json_body['ID'], "status":True}
            return json.dumps(response) 
        elif uri[0]=='service':
            if json_body['ID'] not in self.service_list:
                raise cherrypy.HTTPError(status=400, message='SERVICE NOT REGISTERED')
            if self.reged_service_list[json_body['ID']] == 0:
                self.reged_service_list[json_body['ID']] += 1
                for service in self.config["ServiceList"]:
                    if service["id"] == json_body['ID']:
                        service["register_status"] = True
                with open('catalog/config/catalog.json', 'w') as f:
                    json.dump(self.config, f)
                response = {"service":json_body['ID'], "status":True}
            else:
                response = {"service":json_body['ID'], "status":True}
            return json.dumps(response)
        elif uri[0]=='control':
            if json_body['ID'] not in self.control_list:
                raise cherrypy.HTTPError(status=400, message='DEVICE NOT REGISTERED')
            if self.reged_control_list[json_body['ID']] == 0:
                self.reged_control_list[json_body['ID']] += 1
                for control in self.config["ControlList"]:
                    if control["id"] == json_body['ID']:
                        control["register_status"] = True
                with open('catalog/config/catalog.json', 'w') as f:
                    json.dump(self.config, f)
                response = {"control":json_body['ID'], "status":True}
            else:
                response = {"control":json_body['ID'], "status":True}
            return json.dumps(response)
        else:
            raise cherrypy.HTTPError(status=400, message='INVALID URI')
        
    def startservice(self):
        func_thread = threading.Thread(target=self.check_alive)
        service_thread = threading.Thread(target=self.Service)
        func_thread.start()
        service_thread.start()
        self.func_thread = func_thread
        self.service_thread = service_thread

    def stop(self):
        self.stop_event.set()
        if self.func_thread.is_alive():
            self.func_thread.join()
        cherrypy.engine.stop()
        cherrypy.engine.exit()
        print("Service has been stopped.")

if __name__ == '__main__':
    catalog = Catalog('catalog/config/catalog.json')
    catalog.startservice()
    while True:
        if input("stop running [q]:") == 'q':
            break
    catalog.stop()
    
