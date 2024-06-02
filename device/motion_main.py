import RPi.GPIO as GPIO
import time

class Motion:
    def __init__(self):
        self.motion = 11
        self.led = 18
        self.current_state = 0
        self.last_state = 0
    
    def readStat(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.led, GPIO.OUT)
        GPIO.setup(self.motion, GPIO.IN)
        GPIO.setwarnings(False)
#         try:
#             while True:
        time.sleep(1)
        self.current_state = GPIO.input(self.motion)
        if self.current_state == 1:
            if self.last_state != self.current_state:
                print("Cat at the door!")
                self.last_state = self.current_state
                GPIO.output(self.led,True)
                time.sleep(5)
                return self.current_state
        else:
            if self.last_state != self.current_state:
                print("Cat leave the door!")
                GPIO.output(self.led,False)
                self.last_state = self.current_state
                return self.current_state
    def clean(self):
        GPIO.cleanup()

if __name__ == '__main__':
    motion = Motion()
    try:
        while True:
            state = motion.readStat()
            if state is not None:
                print(f"the current state is: {state}")
    except KeyboardInterrupt:
        pass
    finally:
        motion.motionclean()
    
