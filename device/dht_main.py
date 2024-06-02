import Adafruit_DHT

class DHT11:
    def DHT11_read(self):
        sensor = Adafruit_DHT.DHT11
        pin = 4
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        return humidity, temperature
    
if __name__ == '__main__':
    dht11 = DHT11()
    while True:
        humid,temp = dht11.DHT11_read()
        if humid is not None and temp is not None:
            print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temp, humid))
        else:
            print('Failed to get reading. Try again!')