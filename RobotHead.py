import RPi.GPIO as GPIO
from time import sleep
import json
import subprocess
import requests

GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers

GPIO.setup(17, GPIO.OUT) # GPIO Assign mode
GPIO.setup(21, GPIO.IN)

timeBetweenChecks=1 # Time between robot cycles

json = {}
robot_id = ''

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
    resp = requests.post('http://192.168.0.24:1336/PlantData', json)
    print(json)
    print(resp)
    sleep(timeBetweenChecks) # Wait for next cycle