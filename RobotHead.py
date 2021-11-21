import RPi.GPIO as GPIO
from time import sleep
from threading import Thread
from gpiozero import Button
import json
import subprocess
import requests
import os.path

GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers

# GPIO Assign mode
GPIO.setup(17, GPIO.OUT) # Switch
GPIO.setup(27, GPIO.OUT) # LED
GPIO.setup(21, GPIO.IN) # Water check
button = Button(22) # Button

timeBetweenChecks=1 # Time between robot cycles

json = {}
robot_id = ''

class Bluetooth_init:
    def __init__(self, button_GPIO):
        print("Starting Bluetooth Thread")
        self.button_GPIO = button_GPIO
        self._running = True
        
    def terminate(self):
        self._running = False
        
    def Check_connection_file(self):
        return os.path.isfile("/etc/wpa_supplicant/wpa_supplicant.conf")
        
    def LED_flash(self):
        GPIO.output(27, False)
        sleep(1)
        GPIO.output(27, True)
        sleep(1)
    
    def run(self):
        looking_for_bluetooth = False
        while self._running:
            if self.Check_connection_file() is True:
                button_held = GPIO.input(self.button_GPIO)
                if looking_for_bluetooth is False:
                    print(GPIO.input(self.button_GPIO))
                    if button_held == 1:
                        GPIO.output(27, True)
                    else:
                        looking_for_bluetooth = True
                else:
                    waiting_for_connection_period = 0
                    while waiting_for_connection_period < 11:
                        self.LED_flash()
                        waiting_for_connection_period = waiting_for_connection_period + 1
                    looking_for_bluetooth = False
            else:
                GPIO.output(27, False)

Bluetooth_button_class = Bluetooth_init(22)
Bluetooth_button_thread = Thread(target=Bluetooth_button_class.run)
Bluetooth_button_thread.start()

def getserial():
  # Extract serial from cpuinfo file
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuserial = line[10:26] # Get the serial number of processor
    f.close()
  except:
    cpuserial = "ERROR000000000"
    print("ERROR: No CPU Serial available")
 
  return cpuserial

try:
    robot_id = open("id.txt").read()
    print("INFO: ID present")
except IOError:
    print("Warning: No ID present. Downloading ID")
    file = open("id.txt","w+")
    file.write("1") # TODO: Change it so it automaticly gets a new one via /v1/robots GET

while True:
    value = GPIO.input(21) # Get the water value from plant 
    if (value == 1):
        print("INFO: watering plant...")
        GPIO.output(17, value) # Water the plant
        print("INFO: Sending data to server...")     
        sleep(5)
        GPIO.output(17, 0) # Turn off watering
        print("INFO: waiting for next check")
    else:
        GPIO.output(17, value) # Turn off watering ( just to be sure )
        print("IFNO: not watering this time")
    json = {
        #"name" : "test_user", # TODO: Change it to work with phone app
        #"device_id": robot_id, # Getting ID from file
        "plantId" : 3, # TODO: SChange it to work with phone app
        "value" : value,
    }
    print(json)
    """
    # Commenting because without server it stops working
    resp = requests.post('http://192.168.0.24:1336/PlantData', json)
    print(json)
    print(resp)
    """
    sleep(timeBetweenChecks) # Wait for next cycle