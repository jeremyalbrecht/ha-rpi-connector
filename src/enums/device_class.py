from src.devices.garage import GarageDevice
from src.devices.light import LightDevice
from src.devices.motion import MotionDevice
from src.devices.siren import SirenDevice
from src.devices.strip import StripDevice

DEVICE_CLASSES = {
    "garage": GarageDevice,
    "motion": MotionDevice,
    "light": LightDevice,
    "siren": SirenDevice,
    "strip": StripDevice
}
