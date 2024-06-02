import RPi.GPIO as GPIO
import time

class LED:
    def __init__(self, pin):
        self.led_pin = pin
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.led_pin, GPIO.OUT)
        
    def openled(self, period):
        GPIO.output(self.led_pin, GPIO.HIGH)
        time.sleep(period)
        
    def closeled(self,period):
        GPIO.output(self.led_pin, GPIO.LOW)
        time.sleep(2)
        
    def clean(self):
        GPIO.cleanup()
        
if __name__ == "__main__":
    led1 = LED(36)
    led1.openled(5)
    led1.closeled(5)
    led1.clean()