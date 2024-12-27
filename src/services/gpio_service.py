import logging
import time
from typing import Dict, List, Tuple

from src.enums.gpio_enums import GPIOType, GPIOState

try:
    import RPi.GPIO as GPIO
except ImportError:
    # Fallback for environments without GPIO
    GPIO = None
try:
    from rpi_ws281x import PixelStrip, Color
except ImportError:
    # Fallback for environments without GPIO
    PixelStrip = None
    Color = None

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
        self.objects = {}

        if not self.mock_gpio and GPIO:
            GPIO.setmode(GPIO.BCM)
        for device in devices:
            for gpio in device["gpio"]:
                logger.debug(f"Configuring pin {gpio['gpio']} as {gpio['type']} for device ID {device['id']}")
                if not self.mock_gpio and GPIO:
                    mode = GPIO.IN if gpio["type"] == GPIOType.INPUT else GPIO.OUT
                    GPIO.setup(gpio["gpio"], mode)
                    if "default" in gpio:
                        default_state = GPIO.HIGH if gpio["default"] == GPIOState.HIGH else GPIO.LOW
                        GPIO.output(gpio["gpio"], default_state)

    def read_pin(self, gpio: int) -> int:
        """Read the status of a GPIO pin."""
        if self.mock_gpio:
            logger.debug(f"Mock read GPIO pin {gpio}")
            return 0  # Return default mock value
        return GPIO.input(gpio)

    def write_pin(self, gpio: int, state: str):
        """Write a state (HIGH/LOW) to a GPIO pin."""
        if self.mock_gpio:
            logger.debug(f"Mock write GPIO pin {gpio} to {state}")
            return
        GPIO.output(gpio, GPIO.HIGH if state == "high" else GPIO.LOW)

    def toggle_pin(self, gpio: int, duration: float = 0.5):
        """Toggle a GPIO pin (HIGH -> LOW -> HIGH)."""
        if self.mock_gpio:
            logger.debug(f"Mock toggle GPIO pin {gpio}")
            return
        GPIO.output(gpio, GPIO.LOW)
        time.sleep(duration)
        GPIO.output(gpio, GPIO.HIGH)

    def initialize_strip(self, gpio_pin: int, led_count: int, led_frequency = 800000, led_dma = 10, led_invert = False, led_brightness = 255, led_channel = 0):
        if self.mock_gpio:
            logger.debug(f"Mock initialize LED strip with {led_count} LEDs on GPIO pin {gpio_pin}")
            return
        strip = PixelStrip(led_count, gpio_pin, led_frequency, led_dma, led_invert, led_brightness, led_channel)
        strip.begin()
        self.objects[gpio_pin] = strip

    def set_strip_color(self, gpio: int, position: int, color: Tuple[int, int, int]):
        if self.mock_gpio:
            logger.debug(f"Mock set LED strip color at position {position} to {color}")
            return
        strip = self.objects[gpio]
        strip.setPixelColor(position, Color(*color))
        strip.show()

    def cleanup(self):
        """Clean up GPIO resources."""
        logger.debug("Cleaning up GPIO resources")
        if not self.mock_gpio and GPIO:
            GPIO.cleanup()
