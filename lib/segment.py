from dataclasses import dataclass
import struct

from lib.constant import SYN_FLAG, ACK_FLAG, FIN_FLAG


@dataclass
class SegmentFlag:
    syn: bool
    fin: bool
    ack: bool

    def __init__(self, flag: int):
        self.syn = True if (flag & SYN_FLAG) else False
        self.ack = True if (flag & ACK_FLAG) else False
        self.fin = True if (flag & FIN_FLAG) else False

    def get_flag_bytes(self) -> bytes:
        flag: int = 0

        flag += SYN_FLAG if self.syn else 0
        flag += ACK_FLAG if self.ack else 0
        flag += FIN_FLAG if self.fin else 0

        return struct.pack('!B', flag)
