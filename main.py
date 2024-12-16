import yaml
from gpio_service import GPIOService
from mqtt_service import MQTTService
from device_garage import GarageDevice

from utils.config import get_config
from utils.logger import get_logger
from utils.payload_loader import PayloadLoader


def main():
    logger = get_logger("main")
    config = get_config()
    PayloadLoader.load_payloads()
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

        # Create devices
        devices = []
        for device_config in config["devices"]:
            if device_config["class"] == "garage":
                device = GarageDevice(
                    device_id=device_config["id"],
                    device_class="garage",
                    gpio_service=gpio_service,
                    on_state_change=None,  # Set later by MQTTService
                )
                mqtt_service.register_device_state_change_callback(device)
                devices.append(device)

        mqtt_service.devices = devices

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