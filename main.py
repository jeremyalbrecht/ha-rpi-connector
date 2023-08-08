import sys
import time
import os

import paho.mqtt.client as mqtt
import yaml
from logger import get_logger
from config import get_config
from enums import Topic, Payload
from GPIOService import GPIOService

logger = get_logger("main")
config = get_config()
client = mqtt.Client(client_id="pi3-garage", clean_session=False)
service = GPIOService(config["garages"])


def extract_garage_id(topic: str) -> str:
    return int(topic.split('/')[1])


def on_connect(client, userdata, flags, rc):
    logger.debug("Connected with result code "+str(rc))
    if rc == 0:
        for garage in config["garages"]:
            client.subscribe(Topic.COMMAND_TOPIC.format(garage["id"]))
            client.publish(Topic.AVAILABILITY_TOPIC.format(garage["id"]), Payload.PAYLOAD_AVAILABLE, retain=True)
            logger.debug(f"Marked {garage['id']} available")
    else:
        sys.exit()


def on_message(client, userdata, msg: mqtt.MQTTMessage):
    garage_id = extract_garage_id(msg.topic)
    if msg.payload.decode("utf-8") in [Payload.PAYLOAD_OPEN, Payload.PAYLOAD_STOP, Payload.PAYLOAD_CLOSE]:
        service.trigger(garage_id)

def on_disconnect(client, userdata,rc=0):
    logger.debug("DisConnected result code "+str(rc))


if __name__ == '__main__':
    try:
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_message = on_message
        client.username_pw_set(username=config["mqtt"]["username"], password=config["mqtt"]["password"])
        client.connect(config["mqtt"]["host"], 1883, 60)

        client.loop_start()
        while True:
            service.check_and_publish(client)
            time.sleep(1)
    except KeyboardInterrupt:
        for garage in config["garages"]:
            client.publish(Topic.AVAILABILITY_TOPIC.format(garage["id"]), Payload.PAYLOAD_NOT_AVAILABLE, retain=True)
        client.disconnect()
        client.loop_stop()
        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)

