from src.devices.garage import GarageDevice

DEVICE_CLASSES = {
    "garage": GarageDevice,
    "light": LightDevice,
    "motion": MotionSensorDevice,
    "siren": SirenDevice,
    "strip": StripDevice,
}
