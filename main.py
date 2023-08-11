import sys
import time
import os

import paho.mqtt.client as mqtt
import yaml
from logger import get_logger
from config import get_config
from enums import Topic, Payload
from GPIOService import GPIOService
from mqttService import mqttService

logger = get_logger("main")
config = get_config()
client = mqtt.Client(client_id="pi3-garage", clean_session=False)
service = GPIOService(config["devices"])
mqtt_service = mqttService(config["devices"])


def extract_id(topic: str) -> str:
    return int(topic.split('/')[1])


def on_connect(client, userdata, flags, rc):
    logger.debug("Connected with result code "+str(rc))
    if rc == 0:
        mqtt_service.mark_online(client)
    else:
        sys.exit()


def on_message(client, userdata, msg: mqtt.MQTTMessage):
    device_id = extract_id(msg.topic)
    if msg.payload.decode("utf-8") in [Payload.PAYLOAD_OPEN, Payload.PAYLOAD_CLOSE]:
        service.trigger(device_id, msg.payload.decode("utf-8"))

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
        mqtt_service.mark_offline(client)
        client.disconnect()
        client.loop_stop()
        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)

