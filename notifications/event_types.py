"""The EventType class is declared here, which contains notification types"""
from enum import Enum


class EventTypes(Enum):
    CREATEDEVENT = 1
    REDEEMEDEVENT = 2
    FUNDEDEVENT = 3
    SETUPFAILED = 4
    LIQUIDATED = 5
    STARTEDLIQUIDATION = 6
    REDEMPTIONREQUESTED = 7
    GOTREDEMPTIONSIGNATURE = 8
    PUBKEYREGISTERED = 9
    COURTESYCALLED = 10
    REDEMPTIONFEEINCREASED = 11
    CRATIODECREASED = 12
    NODESTATUS = 13