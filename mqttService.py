import paho.mqtt.client as mqtt
import time
import RPi.GPIO as GPIO

from enums import Topic, Payload, Status, GPIOType, GPIOState, DeviceClass
from logger import get_logger

POLLING_BEFORE_RESET = 600

logger = get_logger("GPIOService")


class mqttService:
    def __init__(self, devices):
        self.devices = devices
        return

    def mark_online(self, client: mqtt.Client):
        for device in self.devices:
            client.subscribe(Topic.COMMAND_TOPIC.format(device["class"], device["id"]))
            client.publish(Topic.AVAILABILITY_TOPIC.format(device["class"], device["id"]), Payload.PAYLOAD_AVAILABLE, retain=True)

    def mark_offline(self, client: mqtt.Client):
        for device in self.devices:
            client.publish(Topic.AVAILABILITY_TOPIC.format(device["class"], device["id"]), Payload.PAYLOAD_NOT_AVAILABLE, retain=True)
