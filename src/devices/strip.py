import threading
import time
from src.devices.base_device import BaseDevice
from src.utils.payload_loader import PayloadLoader

class StripDevice(BaseDevice):

    def __init__(self, device_id: int, device_class: str, gpio_service, on_state_change, custom_vars=None):
        super().__init__(device_id, device_class, gpio_service, on_state_change, custom_vars)
        self.gpio_service.initialize_strip(self._get_gpio("control"), self.custom_vars['num_leds'])
        self.animation_thread = None
        self.stop_animation = threading.Event()
        self.last_applied_color = None

    def handle_command(self, command: str):
        """Handle strip-specific commands."""
        if command == PayloadLoader.get("strip", "color"):
            color = self.custom_vars.get('color', (255, 255, 255))
            for i in range(self.custom_vars['num_leds']):
                self.gpio_service.set_strip_color(self._get_gpio("control"), i, color)
        elif command == PayloadLoader.get("strip", "garage_animation"):
            self.start_animation()
        elif command == PayloadLoader.get("strip", "stop"):
            for i in range(self.custom_vars['num_leds']):
                self.gpio_service.set_strip_color(self._get_gpio("control"), i, (0, 0, 0))
        else:
            raise ValueError(f"Unknown command '{command}' for StripDevice {self.device_id}.")

    def get_status(self) -> str:
        """Return the current status of the strip."""
        if self.animation_thread and self.animation_thread.is_alive():
            return PayloadLoader.get("strip", "running")
        elif self.last_applied_color is not None:
            return PayloadLoader.get("strip", "color")
        else:
            return PayloadLoader.get("strip", "stopped")

    def start_animation(self):
        """Start an animation in a separate thread."""
        if self.animation_thread and self.animation_thread.is_alive():
            self.stop_animation.set()
            self.animation_thread.join()

        self.stop_animation.clear()
        self.animation_thread = threading.Thread(target=self.animate)
        self.animation_thread.start()

    def animate(self):
        """Run a simple animation."""
        while not self.stop_animation.is_set():
            for i in range(self.custom_vars['num_leds']):
                if self.stop_animation.is_set():
                    break
                self.gpio_service.set_strip_color(self._get_gpio("control"), i, (255, 0, 0))  # Red color
                time.sleep(0.05)
                self.gpio_service.set_strip_color(self._get_gpio("control"), i, (0, 0, 0))  # Turn off
                time.sleep(0.05)