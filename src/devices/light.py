from src.devices.base_device import BaseDevice
from src.enums.gpio_enums import GPIOState
from src.services.gpio_service import GPIOService
from src.utils.payload_loader import PayloadLoader


class LightDevice(BaseDevice):

    def __init__(self, device_id: int, device_class: str, gpio_service: GPIOService, on_state_change):
        super().__init__(device_id, device_class, gpio_service, on_state_change)
        self.status = None

    def get_status(self) -> str:
        return self.status

    def handle_command(self, command: str):
        """Handle garage-specific commands like open/close."""
        if command == PayloadLoader.get("light", "on"):
            self.status = GPIOState.HIGH
            self.write_status("control", GPIOState.HIGH)
        elif command == PayloadLoader.get("light", "off"):
            self.status = GPIOState.LOW
            self.write_status("control", GPIOState.LOW)
        else:
            raise ValueError(f"Unknown command '{command}' for LightDevice {self.device_id}.")
        self.notify_state_change()