from abc import ABC, abstractmethod
from collections.abc import Callable

from src.services.gpio_service import GPIOService


class BaseDevice(ABC):
    """Abstract base class for all devices."""

    def __init__(self, device_id: int, device_class: str, gpio_service: GPIOService, on_state_change: Callable,
                 custom_vars: dict = None):
        self.device_id = device_id
        self.device_class = device_class
        self.gpio_service = gpio_service
        self.topics = {
            "availability": f"{self.device_class}/{self.device_id}/availability",
            "command": f"{self.device_class}/{self.device_id}/set",
            "state": f"{self.device_class}/{self.device_id}/status"
        }
        self._on_state_change = on_state_change
        self.custom_vars = custom_vars if custom_vars is not None else {}

    @abstractmethod
    def handle_command(self, command: str):
        """Process a command specific to the device."""
        pass

    @abstractmethod
    def get_status(self) -> str:
        """Return the current status of the device."""
        pass

    def notify_state_change(self, state: str = None):
        """
        Notify the state change to the callback.
        :param state: Optional state to be notified. If None, calls get_status().
        """
        if self._on_state_change:
            actual_state = state if state is not None else self.get_status()
            self._on_state_change(self.device_class, self.device_id, actual_state)

    def get_topic(self, topic_type):
        if topic_type not in self.topics:
            raise ValueError(f"Invalid topic type: {topic_type}")
        return self.topics[topic_type]

    def read_status(self, pin_name: str) -> int:
        """Read the status of a GPIO pin."""
        gpio = self._get_gpio(pin_name)
        return self.gpio_service.read_pin(gpio)

    def write_status(self, pin_name: str, state: str):
        """Write a state to a GPIO pin."""
        gpio = self._get_gpio(pin_name)
        self.gpio_service.write_pin(gpio, state)

    def toggle_control(self, pin_name: str, duration: float = 0.5):
        """Toggle a control pin."""
        gpio = self._get_gpio(pin_name)
        self.gpio_service.toggle_pin(gpio, duration)

    def _get_gpio(self, pin_name: str) -> int:
        """Retrieve GPIO pin number by name."""
        device = next((device for device in self.gpio_service.devices if device['id'] == self.device_id and device['class'] == self.device_class), None)
        if not device:
            raise ValueError(f"Device '{self.device_id}' not found.")
        pin = next((gpio for gpio in device['gpio'] if gpio["name"] == pin_name), None)
        if not pin:
            raise ValueError(f"Pin '{pin_name}' not found for device {self.device_id}.")
        return pin["gpio"]