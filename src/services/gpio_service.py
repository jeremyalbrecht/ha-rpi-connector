import logging
import time
from typing import Dict, List

from src.enums.gpio_enums import GPIOType, GPIOState

try:
    import RPi.GPIO as GPIO
except ImportError:
    # Fallback for environments without GPIO
    GPIO = None

logger = logging.getLogger("GPIOService")


class GPIOService:
    """Service to manage GPIO operations."""

    def __init__(self, devices: List[Dict], mock_gpio: bool = False):
        """
        Initialize GPIOService.
        :param devices: List of device configurations.
        :param mock_gpio: If True, GPIO operations are mocked.
        """
        self.devices = devices
        self.mock_gpio = mock_gpio
        self.previous_status = {}

        if not self.mock_gpio and GPIO:
            GPIO.setmode(GPIO.BCM)
            for device in devices:
                for gpio in device["gpio"]:
                    mode = GPIO.IN if gpio["type"] == GPIOType.INPUT else GPIO.OUT
                    GPIO.setup(gpio["gpio"], mode)
                    if "default" in gpio:
                        default_state = GPIO.HIGH if gpio["default"] == GPIOState.HIGH else GPIO.LOW
                        GPIO.output(gpio["gpio"], default_state)

    def read_pin(self, gpio: int) -> int:
        """Read the status of a GPIO pin."""
        if self.mock_gpio:
            logger.info(f"Mock read GPIO pin {gpio}")
            return 0  # Return default mock value
        return GPIO.input(gpio)

    def write_pin(self, gpio: int, state: str):
        """Write a state (HIGH/LOW) to a GPIO pin."""
        if self.mock_gpio:
            logger.info(f"Mock write GPIO pin {gpio} to {state}")
            return
        GPIO.output(gpio, GPIO.HIGH if state == "high" else GPIO.LOW)

    def toggle_pin(self, gpio: int, duration: float = 0.5):
        """Toggle a GPIO pin (HIGH -> LOW -> HIGH)."""
        if self.mock_gpio:
            logger.info(f"Mock toggle GPIO pin {gpio}")
            return
        GPIO.output(gpio, GPIO.LOW)
        time.sleep(duration)
        GPIO.output(gpio, GPIO.HIGH)

    def cleanup(self):
        """Clean up GPIO resources."""
        if not self.mock_gpio and GPIO:
            GPIO.cleanup()
