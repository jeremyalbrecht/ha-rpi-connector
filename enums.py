from enum import Enum


class GPIOType(str, Enum):
    INPUT = "input"
    OUTPUT = "output"


class GPIOState(str, Enum):
    HIGH = "high"
    LOW = "low"


class Status(int, Enum):
    OPEN = 1
    CLOSED = 0


class DeviceClass(str, Enum):
    GARAGE = "garage"
    MOTION = "motion"
    SIREN = "siren"
    LIGHT = "light"

class Topic(str, Enum):
    AVAILABILITY_TOPIC = "{}/{}/availability"
    COMMAND_TOPIC = "{}/{}/set"
    STATE_TOPIC = "{}/{}/status"


class Payload(str, Enum):
    OFF = "OFF"
    ON = "ON"
    PAYLOAD_OPEN = "OPEN"
    PAYLOAD_CLOSE = "CLOSE"
    PAYLOAD_STOP = "STOP"
    STATE_OPEN = "open"
    STATE_OPENING = "opening"
    STATE_CLOSED = "closed"
    STATE_CLOSING = "closing"
    PAYLOAD_AVAILABLE = "online"
    PAYLOAD_NOT_AVAILABLE = "offline"
