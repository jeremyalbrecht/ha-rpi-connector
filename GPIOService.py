import json

import paho.mqtt.client as mqtt
import time
import RPi.GPIO as GPIO

from enums import Topic, Payload, Status, GPIOType, GPIOState, DeviceClass
from logger import get_logger

POLLING_BEFORE_RESET = 600

logger = get_logger("GPIOService")


class GPIOService:
    def __init__(self, devices):
        self.devices = devices
        self.polling = 0
        self.previous_status = {}
        GPIO.setmode(GPIO.BCM)
        for device in devices:
            for gpio in device["gpio"]:
                GPIO.setup(gpio['gpio'], GPIO.IN if gpio["type"] == GPIOType.INPUT else GPIO.OUT)
                if "default" in gpio:
                    GPIO.output(gpio['gpio'], GPIO.HIGH if gpio["default"] == GPIOState.HIGH else GPIO.LOW)
                if gpio["type"] == GPIOType.INPUT:
                    self.previous_status[device["id"]] = None

    def reset_polling(self):
        for device in self.devices:
            self.previous_status[device["id"]] = None

    def update_master(self, device, status, client: mqtt.Client):
        client.publish(Topic.STATE_TOPIC.format(device["class"], device["id"]),
                       Payload.STATE_OPEN if status == Status.OPEN else Payload.STATE_CLOSED, retain=True, qos=2)
        self.previous_status[device["id"]] = status

    def check_and_publish(self, client: mqtt.Client):
        self.polling += 1
        if self.polling > POLLING_BEFORE_RESET:
            self.reset_polling()
        for device in self.devices:
            status_pin = [gpio for gpio in device["gpio"] if gpio["name"] == "status"]
            if "no_update_before" in device and time.time() <= device["no_update_before"]:
                continue
            if len(status_pin) == 1:
                status_pin = status_pin[0]
                status = GPIO.input(status_pin["gpio"])
                if status != self.previous_status[device["id"]]:
                    device["no_update_before"] = time.time() + 30
                    self.update_master(device, status, client)

    def trigger(self, device_id: str, order: Payload, client: mqtt.Client):
        device = [d for d in self.devices if d["id"] == device_id]
        if len(device) == 1:
            device = device[0]
            if device["class"] == DeviceClass.GARAGE:
                if (self.previous_status[device["id"]] == Status.OPEN and order == Payload.PAYLOAD_CLOSE) or \
                        (self.previous_status[device["id"]] == Status.CLOSED and order == Payload.PAYLOAD_OPEN):
                    control_pin = [gpio for gpio in device["gpio"] if gpio["name"] == "control"]
                    if len(control_pin) == 1:
                        control_pin = control_pin[0]
                        GPIO.output(control_pin["gpio"], GPIO.HIGH)
                        GPIO.output(control_pin["gpio"], GPIO.LOW)
                        time.sleep(0.5)
                        GPIO.output(control_pin["gpio"], GPIO.HIGH)
                        client.publish(Topic.STATE_TOPIC.format(DeviceClass.GARAGE, device["id"]),
                                       Payload.STATE_OPENING if self.previous_status[device["id"]] == Status.CLOSED else Payload.STATE_CLOSING, retain=True, qos=2)
                        device["no_update_before"] = time.time() + 10
                        self.reset_polling()

    def triggerJSON(self, device_id: str, order: str, client: mqtt.Client):
        device = [d for d in self.devices if d["id"] == device_id]
        message = json.loads(order)
        if len(device) == 1:
            device = device[0]
            if device["class"] == DeviceClass.SIREN:
                control_pin = [gpio for gpio in device["gpio"] if gpio["name"] == "control"]
                if len(control_pin) == 1:
                    control_pin = control_pin[0]
                    GPIO.output(control_pin["gpio"], GPIO.HIGH if message["state"] == Payload.PAYLOAD_OPEN else GPIO.LOW)
                    client.publish(Topic.STATE_TOPIC.format(device["class"], device["id"]),
                                   Payload.STATE_OPEN if message["state"] == Payload.PAYLOAD_OPEN else Payload.STATE_CLOSED,
                                   retain=True, qos=2)
            elif device["class"] == DeviceClass.LIGHT:
                control_pin = [gpio for gpio in device["gpio"] if gpio["name"] == "control"]
                if len(control_pin) == 1:
                    control_pin = control_pin[0]
                    GPIO.output(control_pin["gpio"],
                                GPIO.HIGH if message["state"] == Payload.ON else GPIO.LOW)
                    client.publish(Topic.STATE_TOPIC.format(device["class"], device["id"]),
                                   "{\"state\": {}}".format(Payload.ON if message["state"] == Payload.ON else Payload.OFF),
                                   retain=True, qos=2)