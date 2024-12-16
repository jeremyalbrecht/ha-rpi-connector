import os
import time
import socket
import sys

import RPi.GPIO as GPIO
from pirc522 import RFID
import paho.mqtt.client as mqtt

from utils.logger import get_logger
from utils.config import get_config


logger = get_logger("rfid")
config = get_config()
client = mqtt.Client(client_id=socket.gethostname() + '-rfid', clean_session=False)
rc522 = RFID()

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)


def on_connect(client, userdata, flags, rc):
    logger.debug("Connected with result code "+str(rc))
    if rc != 0:
        sys.exit()


def on_disconnect(client, userdata,rc=0):
    logger.debug("DisConnected result code "+str(rc))


if __name__ == '__main__':
    try:
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.username_pw_set(username=config["mqtt"]["username"], password=config["mqtt"]["password"])
        client.connect(config["mqtt"]["host"], config["mqtt"]["port"], 60)

        client.loop_start()
        while True:
            rc522.wait_for_tag()
            (error, tag_type) = rc522.request()
            if not error:
                (error, uid) = rc522.anticoll()
                if not error:
                    id = (int.from_bytes(uid[0:4], 'big'))
                    client.publish(config["rfid"]["topic"], id, retain=True)
                    time.sleep(1)
    except KeyboardInterrupt:
        client.disconnect()
        client.loop_stop()
        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)