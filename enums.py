from enum import Enum


class Topic(str, Enum):
    AVAILABILITY_TOPIC = "garage/{}/availability"
    COMMAND_TOPIC = "garage/{}/set"
    STATE_TOPIC = "garage/{}/status"


class Payload(str, Enum):
    PAYLOAD_OPEN = "OPEN"
    PAYLOAD_CLOSE = "CLOSE"
    PAYLOAD_STOP = "STOP"
    STATE_OPEN = "open"
    STATE_OPENING = "opening"
    STATE_CLOSED = "closed"
    STATE_CLOSING = "closing"
    PAYLOAD_AVAILABLE = "online"
    PAYLOAD_NOT_AVAILABLE = "offline"