from src.devices.base_device import BaseDevice
from src.enums.gpio_enums import GPIOState
from src.services.gpio_service import GPIOService
from src.utils.payload_loader import PayloadLoader


class MotionDevice(BaseDevice):

    def __init__(self, device_id: int, device_class: str, gpio_service: GPIOService, on_state_change, custom_vars=None):
        super().__init__(device_id, device_class, gpio_service, on_state_change)
        self.status = None

    def get_status(self) -> str:
        return PayloadLoader.get("motion", "detected") if self.read_status("status") else PayloadLoader.get("motion", "free")

    def handle_command(self, command: str):
        raise ValueError(f"MotionDevice is a read-only device.")