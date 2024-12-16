from enum import Enum

class DeviceClass(str, Enum):
    GARAGE = "garage"
    MOTION = "motion"
    SIREN = "siren"
    LIGHT = "light"
    STRIP = "strip"