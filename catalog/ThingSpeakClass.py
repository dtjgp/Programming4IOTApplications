'''
 	Thingspeak is a third-party software (https://thingspeak.com/) that provides REST Web Services.
    It is an open-data platform for the Internet of Things to store, post-process and visualize the humidity and temperature data (through plots).
'''

import json
import os
import requests
import paho.mqtt.publish as publish
import random
import time

# Class to handle the ThingSpeak configuration
class ThingSpeak():
    def __init__(self, TSfile, channel_info=None, name=None):
        self.config = TSfile
        self.URL = self.config['URL']
        self.REST_APIKey = self.config['REST_apikey']
        self.public_flag = self.config['public_flag']
        self.MQTT_broker = self.config['MQTT_broker']
        self.MQTT_port = self.config['MQTT_port']
        self.MQTT_protocol = self.config['MQTT_protocol']
        self.MQTT_id = self.config['MQTT_id']
        self.MQTT_username = self.config['MQTT_username']
        self.MQTT_password = self.config['MQTT_password']
        if channel_info and not name:
            with open(channel_info, 'r') as file:
                self.ChannelInfo = json.load(file)
        elif name and not channel_info:
            self.create_channel(name)
        else:
            raise ValueError('Provide either channel_info file or name, not both')
        
    # method to create a new channel
    def create_channel(self,name):
        channel_url = self.URL + '.json'
        fields = ['Temperature', 'Humidity', 'Toilet_status', \
                  'Door_status', 'kitchen_status', "Air_conditioner_status", \
                  'Light_status', 'Dehumidifier_status']
        context ={
            "api_key": self.REST_APIKey,
            "name": name,
            "public_flag": self.public_flag,
            "field1": fields[0],
            "field2": fields[1],
            "field3": fields[2],
            "field4": fields[3],
            "field5": fields[4],
            "field6": fields[5],
            "field7": fields[6],
            "field8": fields[7]
        }
        try:
            response = requests.post(channel_url, data = context).text
            self.ChannelInfo = json.loads(response)
            print(self.ChannelInfo)
            # save the channel info to a file
            with open(f'config/{name}.json', 'w') as file:
                json.dump(self.ChannelInfo, file)   
        except requests.RequestException as e:
            print("Failed to create channel: ", e)
        
    # method to update the channel, using mqtt protocol
    # it is the connection between thingspeak and the broker
    def publishdata(self, temp=None, humi=None, toilet=None, door=None, kit=None, \
                        aircon=None, light=None, dehumi=None):
        # add the channel to the MQTT broker
        # Your MQTT credentials for the device
        mqtt_client_ID = self.MQTT_id
        mqtt_username  = self.MQTT_username
        mqtt_password  = self.MQTT_password
        # print(f'the mqtt_username is: {mqtt_username}, the mqtt_password is: {mqtt_password}')
        channelID = self.ChannelInfo['id']
        api_key = self.ChannelInfo['api_keys'][0]['api_key']
        # print(f"Channel ID: {channelID}, API Key: {api_key}")
        topic = "channels/" + str(channelID) + "/publish" 
        payload = "field1=" + str(temp) + "&field2=" + str(humi) + \
                  "&field3=" + str(toilet) + "&field4=" + str(door) + "&field5=" + str(kit)+ \
                  "&field6=" + str(aircon) + "&field7=" + str(light) + "&field8=" + str(dehumi)
        auth = {
            'username': mqtt_username,
            'password': mqtt_password
        }
        print('Publishing data to ThingSpeak...')
        publish.single(topic, payload, hostname=self.MQTT_broker, \
                       port=self.MQTT_port, transport=self.MQTT_transport,client_id=mqtt_client_ID, auth=auth)
        print('Data published!')

    # method to delete the channel
    def deletechannel(self):
        channel_url = self.URL + '/' + str(self.ChannelInfo['id']) + '.json'
        print(f"Deleting channel {self.ChannelInfo['name']}...")
        context = {"api_key": self.REST_APIKey}
        info_post = requests.delete(channel_url, data = context).text
        print(info_post)
        print(f"Channel {self.ChannelInfo['name']} deleted!")
    
    # method to check the channel info
    def getfeeds(self):
        # read a channel feed
        channel_url = self.URL + '/' + str(self.ChannelInfo['id']) + '/feeds.json'
        response = requests.get(channel_url).text
        # create a json object from the response to store the feeds
        feeds = json.loads(response)['feeds']
        # print(feeds)
        # print the feeds
        for feed in feeds:
            print(f"Feed ID: {feed['entry_id']}, Created at: {feed['created_at']}, \
                    Field1: {feed['field1']}, Field2: {feed['field2']}, Field3: {feed['field3']},\
                    Field4: {feed['field4']}, Field5: {feed['field5']}")
        return feeds
    
    # method to read the channel field
    def getfield(self,num):
        channel_url = self.URL + '/' + str(self.ChannelInfo['id']) + '/fields/'+ str(num)+ '.json'
        response = requests.get(channel_url).text
        selected_field = json.loads(response)['feeds']
        # print(selected_field)
        return selected_field
    
    # method to read the channel status
    def getstatus(self):
        channel_url = self.URL + '/' + str(self.ChannelInfo['id']) + 'status.json'
        response = requests.get(channel_url).text
        channel_status = json.loads(response)
        print(channel_status)
        # read the channel status
        for key, value in channel_status.items():
            print(f"{key}: {value}")
        # print(f"Channel ID: {channel_status['id']}, Name: {channel_status['name']}, Public: {channel_status['public_flag']}")
        return channel_status 
    
            
        
    

if __name__ == '__main__':
    # check if the ThingSpeak.json is in the dir
    working_dir = os.getcwd()
    print(f'The current working dir is: {working_dir}')
    TSfile = 'config/ThingSpeak.json'
    channel_info1 = 'config/Room1.json'
    name = 'Room1'
    # create a new channel
    ch1 = ThingSpeak(TSfile, channel_info=channel_info1)
    print(ch1.ChannelInfo['id'])
    # ch1feeds = ch1.getfeeds()
    # print(ch1feeds)
    # ch1_field2 = ch1.getfield(2)
    # print(ch1_field2)
    # ch1.publishdata(2,2,2,12,2)
    # ch1_status = ch1.getstatus()
    # print(ch1_status)
    # ch1.deletechannel()
    
 
    