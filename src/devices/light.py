import json
import threading
import time

from src.devices.base_device import BaseDevice
from src.enums.gpio_enums import GPIOState
from src.services.gpio_service import GPIOService
from src.utils.payload_loader import PayloadLoader


class LightDevice(BaseDevice):

    def __init__(self, device_id: int, device_class: str, gpio_service: GPIOService, on_state_change, custom_vars=None):
        super().__init__(device_id, device_class, gpio_service, on_state_change, custom_vars)
        self.status = None
        self.brightness = 255
        self.cleaning_thread = None
        self.stop_flash = threading.Event()


    def get_status(self) -> str:
        return json.dumps({
            "state": PayloadLoader.get("light", "on") if self.status == GPIOState.HIGH else PayloadLoader.get("light", "off"),
        })

    def handle_command(self, command: str):
        """Handle garage-specific commands like open/close."""
        payload = json.loads(command)
        if payload['state'] == PayloadLoader.get("light", "on"):
            self.status = GPIOState.HIGH
            self.write_status("control", self.status)
        elif payload['state'] == PayloadLoader.get("light", "off"):
            self.status = GPIOState.LOW
            self.write_status("control", self.status)
        if 'brightness' in payload:
            self.brightness = payload['brightness']
            raise ValueError(f"Brightness control not implemented yet.")
        if 'flash' in payload:
            self.status = GPIOState.HIGH
            self.write_status("control", self.status)
            if self.cleaning_thread and self.cleaning_thread.is_alive():
                self.stop_flash.set()
                self.cleaning_thread.join()

            self.stop_flash.clear()
            self.cleaning_thread = threading.Thread(target=self.clean_light_after, args=(payload['flash']))
            self.cleaning_thread.start()

        self.notify_state_change()

    def clean_light_after(self, duration: float):
        start = time.time()
        while time.time() - start < duration:
            if self.stop_flash.is_set():
                break
            time.sleep(0.1)
        self.status = GPIOState.LOW
        self.write_status("control", self.status)