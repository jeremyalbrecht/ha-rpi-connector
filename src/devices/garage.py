from src.devices.base_device import BaseDevice
from src.utils.payload_loader import PayloadLoader


class GarageDevice(BaseDevice):

    def handle_command(self, command: str):
        """Handle garage-specific commands like open/close."""
        if command == PayloadLoader.get("garage", "open"):
            self.toggle_control("control")
            self.notify_state_change(PayloadLoader.get("garage", "state_opening"))
        elif command == PayloadLoader.get("garage", "close"):
            self.toggle_control("control")
            self.notify_state_change(PayloadLoader.get("garage", "state_closing"))
        else:
            raise ValueError(f"Unknown command '{command}' for GarageDevice {self.device_id}.")

    def get_status(self) -> str:
        """Return the current status of the garage door."""
        status_pin = self.read_status("status")
        return PayloadLoader.get("garage", "state_open") if status_pin == 1 else PayloadLoader.get("garage", "state_closed")