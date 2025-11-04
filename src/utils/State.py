from enum import StrEnum, auto

class State(StrEnum):
    DISARMED = auto()
    ARMING = auto()
    ARMED = auto()
    DISARMING = auto()
    ALERT = auto()