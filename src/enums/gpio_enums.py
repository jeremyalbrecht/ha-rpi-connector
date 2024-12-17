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
