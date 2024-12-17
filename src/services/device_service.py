from src.enums.device_class import DEVICE_CLASSES


class DeviceService:
    """
    Manages the initialization and interactions of all devices based on the configuration.
    """

    def __init__(self, config, gpio_service, mqtt_service):
        """
        Initializes the device manager.

        Args:
            config (dict): Configuration for all devices.
            gpio_service (GPIOService): The GPIO service instance for hardware control.
            mqtt_service (MQTTService): The MQTT service instance for message routing.
        """
        self.devices = []
        self.gpio_service = gpio_service
        self.mqtt_service = mqtt_service

        # Initialize devices based on configuration
        for device_config in config["devices"]:
            device_class = device_config["class"]
            device_id = device_config["id"]

            # Look up the corresponding device class
            device_type = DEVICE_CLASSES.get(device_class)
            if device_type:
                # Instantiate the device
                device = device_type(
                    device_id=device_id,
                    device_class=device_class,
                    gpio_service=gpio_service,
                    on_state_change=mqtt_service.handle_device_state_change,
                )
                self.devices.append(device)
            else:
                raise ValueError(f"Unsupported device class: {device_class}")