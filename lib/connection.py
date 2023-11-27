import struct
from abc import ABC, abstractmethod
from dataclasses import dataclass

from lib.constant import SEGMENT_SIZE
from lib.exception import InvalidChecksumError
from lib.segment import Segment, SegmentFlag
import socket


@dataclass
class MessageInfo:
    ip: str
    port: int
    segment: Segment

    def __init__(self, ip: str, port: int, segment: Segment):
        self.ip = ip
        self.port = port
        self.segment = segment

