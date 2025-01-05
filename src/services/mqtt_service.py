import logging
from datetime import datetime, timedelta

import paho.mqtt.client as mqtt
import time
import socket
from threading import Thread, Event

logger = logging.getLogger("MQTTService")


class MQTTService:
    """Service to manage MQTT communication."""

    def __init__(self, host: str, port: int, username: str, password: str, devices: list, interval: int = 10):
        """
        Initialize MQTTService.
        :param host: MQTT broker host.
        :param port: MQTT broker port.
        :param username: MQTT username.
        :param password: MQTT password.
        :param devices: List of device instances.
        :param interval: Interval for periodic status publishing (seconds).
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.devices = devices
        self.interval = interval

        self.client = mqtt.Client(client_id=socket.gethostname(), clean_session=False)
        self.stop_event = Event()
        self.delay_end_times = {}

        self.client.username_pw_set(username, password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.last_status = {}

    def on_connect(self, client, userdata, flags, rc):
        """Handle connection to MQTT broker."""
        if rc == 0:
            logger.info("Connected to MQTT broker.")
            for device in self.devices:
                topic = device.get_topic("command")
                client.subscribe(topic)
                logger.info(f"Subscribed to {topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")

    def on_message(self, client, userdata, msg):
        """Route incoming MQTT messages to the correct device."""
        logger.debug("Received message: %s", msg.payload)
        topic_parts = msg.topic.split("/")
        if len(topic_parts) == 3 and topic_parts[-1] == "set":
            device_class, device_id, _ = topic_parts
            for device in self.devices:
                if device.device_class == device_class and str(device.device_id) == device_id:
                    device.handle_command(msg.payload.decode())
                    return
            logger.warning(f"No matching device for topic: {msg.topic}")

    def start(self):
        """Start the MQTT service and the status publishing thread."""
        self.client.connect(self.host, self.port)
        self.client.loop_start()
        self.publish_availability("online")
        if self.interval > 0:
            self.status_thread = Thread(target=self.publish_status_periodically)
            self.status_thread.start()

    def stop(self):
        """Stop the MQTT service and threads."""
        self.publish_availability("offline")
        self.stop_event.set()
        if self.interval > 0:
            self.status_thread.join()
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("MQTT service stopped.")

    def delay_updates(self, device_identifier: str, delay_seconds: int):
        """Delay updates for a specific device for a given amount of time."""
        self.delay_end_times[device_identifier] = datetime.now() + timedelta(seconds=delay_seconds)
        logger.info(f"Updates for device {device_identifier} delayed for {delay_seconds} seconds.")

    def publish(self, topic: str, payload: str, retain: bool = False):
        """Publish a message to a specific topic."""
        self.client.publish(topic, payload, retain=retain, qos=2)
        logger.info(f"Published to {topic}: {payload}")

    def publish_status(self):
        """Publish the current status of all devices."""
        for device in self.devices:
            if device.identifier() in self.delay_end_times and datetime.now() < self.delay_end_times[device.identifier()]:
                continue
            status = device.get_status()
            if device.identifier() in self.last_status and self.last_status[device.identifier()] == status:
                continue
            topic = device.get_topic("status")
            self.last_status[device.identifier()] = status
            self.client.publish(topic, status, retain=True, qos=2)
            logger.info(f"Published status for {device.device_class} {device.device_id}: {status}")

    def publish_status_periodically(self):
        """Publish status at regular intervals."""
        while not self.stop_event.is_set():
            self.publish_status()
            time.sleep(self.interval)

    def register_device_state_change_callback(self, device):
        """Register a state change callback for a device."""
        device._on_state_change = self.handle_device_state_change

    def handle_device_state_change(self, device_class, device_id, status):
        """Handle a state change event from a device."""
        identifier = f"{device_class}_{device_id}"
        if identifier in self.delay_end_times and datetime.now() < self.delay_end_times[identifier]:
            return
        topic = f"{device_class}/{device_id}/status"
        self.publish(topic, status)

    def publish_availability(self, state: str):
        """Publish the availability status of all devices to Home Assistant."""
        for device in self.devices:
            topic = device.get_topic("availability")
            self.publish(topic, state, retain=True)
            logger.info(f"Published availability for {device.device_class} {device.device_id}: {state}")
