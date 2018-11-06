#!/usr/bin/python

from subprocess import call
import sys
import time
import ConfigParser
import logging
import RPi.GPIO as GPIO

# Global Vars
bashbot = False
bashbot_ch = ""
bashbot_msg = ""

# Pin Definitons:
butPin = 21
lightPin1 = 20
lightPin2 = 26
buzPin1 = 16
buzPin2 = 19

# Pin Set
GPIO.setup(butPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(lightPin1, GPIO.OUT)
GPIO.setup(lightPin2, GPIO.OUT)
GPIO.setup(buzPin1, GPIO.OUT)
GPIO.setup(buzPin2, GPIO.OUT)

# Pin Initial State
GPIO.output(lightPin1, GPIO.LOW)
GPIO.output(lightPin2, GPIO.LOW)
GPIO.output(buzPin1, GPIO.LOW)
GPIO.output(buzPin2, GPIO.LOW)

def main_loop():
    print("The doorbell is listening! Press CTRL+C to exit")
    while 1:
        if GPIO.input(butPin):
            logging.info("Doorbell Rang")
            door_ring()
            notify_slack()
            door_ring()
            while GPIO.input(butPin):
                time.sleep(0.05)
            
def door_ring():
    GPIO.output(buzPin1, GPIO.HIGH)
    GPIO.output(buzPin2, GPIO.HIGH)
    GPIO.output(lightPin1, GPIO.HIGH)
    time.sleep(0.25)
    GPIO.output(lightPin1, GPIO.LOW)
    GPIO.output(lightPin2, GPIO.HIGH)
    time.sleep(0.25)
    GPIO.output(lightPin2, GPIO.LOW)
    GPIO.output(buzPin1, GPIO.LOW)
    GPIO.output(buzPin2, GPIO.LOW)
    
def notify_slack():
    try:
        if bashbot == True:
            call(['bashbot', bashbot_ch , bashbot_msg])
    except:
        logging.error("Error calling bashbot")
    
def get_config():
    config = ConfigParser.RawConfigParser()
    config.read('doorbell.properties')
    global bashbot_ch
    bashbot_ch = config.get('bashbot', 'bashbot.channel')
    global bashbot_msg
    bashbot_msg = config.get('bashbot', 'bashbot.message')
    
    if bashbot_ch == "":
        global bashbot
        bashbot = True
        logging.info("bashbot is on")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        get_config()
        main_loop()
    except KeyboardInterrupt:
        print >> sys.stderr, '\nExiting doorbell.\n'
        GPIO.cleanup() # cleanup all GPIO
        sys.exit(0)
