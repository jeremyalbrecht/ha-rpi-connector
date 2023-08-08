import paho.mqtt.client as mqtt
import time
import RPi.GPIO as GPIO

from enums import Topic, Payload
from logger import get_logger

POLLING_BEFORE_RESET = 600

logger = get_logger("GPIOService")

class GPIOService:
    def __init__(self, garages):
        self.garages = garages
        self.polling = 0
        self.previous_status = {}
        for garage in garages:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(garage['status'], GPIO.IN)
            GPIO.setup(garage['control'], GPIO.OUT)
            GPIO.output(garage['control'], GPIO.HIGH)
            self.previous_status[garage["id"]] = None

    def reset_polling(self):
        for garage in self.garages:
            self.previous_status[garage["id"]] = None

    def update_master(self, garage, status, client: mqtt.Client):
        client.publish(Topic.STATE_TOPIC.format(garage["id"]), Payload.STATE_OPEN if status == 1 else Payload.STATE_CLOSED, retain=True, qos=2)
        self.previous_status[garage["id"]] = status

    def check_and_publish(self, client: mqtt.Client):
        self.polling += 1
        if self.polling > POLLING_BEFORE_RESET:
            self.reset_polling()
        for garage in self.garages:
            status = GPIO.input(garage['status'])
            if status != self.previous_status[garage["id"]]:
                self.update_master(garage, status, client)

    def trigger(self, garage_id: str):
        for garage in self.garages:
            if garage["id"] == garage_id:
                GPIO.output(garage['control'], GPIO.HIGH)
                GPIO.output(garage['control'], GPIO.LOW)
                time.sleep(0.5)
                GPIO.output(garage['control'], GPIO.HIGH)
                break
