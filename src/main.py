import os
from pathlib import Path

from services.device_service import DeviceService
from services.gpio_service import GPIOService
from services.mqtt_service import MQTTService
from utils.config import get_config
from utils.logger import get_logger
from utils.payload_loader import PayloadLoader


def main():
    logger = get_logger("main")
    config = get_config()
    PayloadLoader.load_payloads(Path(os.getcwd(), "conf", "payloads.yaml"))
    gpio_service = GPIOService(devices=config["devices"], mock_gpio=config.get("mock_gpio", False))

    try:
        # Initialize MQTT Service
        mqtt_service = MQTTService(
            host=config["mqtt"]["host"],
            port=config["mqtt"]["port"],
            username=config["mqtt"]["username"],
            password=config["mqtt"]["password"],
            devices=[],
            interval=10
        )

        device_manager = DeviceService(config, gpio_service, mqtt_service)

        mqtt_service.devices = device_manager.devices

        mqtt_service.start()

        # Keep the program running
        while True:
            pass

    except KeyboardInterrupt:
        logger.info("Shutting down services.")
        mqtt_service.stop()
        gpio_service.cleanup()


if __name__ == "__main__":
    main()