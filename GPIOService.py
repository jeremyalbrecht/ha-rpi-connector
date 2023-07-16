import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

from enums import Topic, Payload

POLLING_BEFORE_RESET = 600


class GPIOService:
    def __init__(self, garages):
        self.garages = garages
        self.polling = 0
        self.previous_status = {}
        for garage in garages:
            GPIO.setup(garage['status'], GPIO.IN)
            self.previous_status[garage["id"]] = None

    def reset_polling(self):
        for garage in self.garages:
            self.previous_status[garage["id"]] = None

    def update_master(self, garage, status, client: mqtt.Client):
        client.publish(Topic.STATE_TOPIC.format(garage["id"]), Payload.STATE_OPEN if status == 0 else Payload.STATE_CLOSED)
        self.previous_status[garage["id"]] = status

    def check_and_publish(self, client: mqtt.Client):
        self.polling += 1
        if self.polling > POLLING_BEFORE_RESET:
            self.reset_polling()
        for garage in self.garages:
            status = GPIO.input(garage['status'])
            if status != self.previous_status[garage["id"]]:
                self.update_master(garage, status, client)
