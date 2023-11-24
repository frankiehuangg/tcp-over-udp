from constants import SYN_FLAG, ACK_FLAG, FIN_FLAG
import struct

class SegmentFlag:
    def __init__(self, flag: bytes = 0b0):
        self.syn = flag & SYN_FLAG
        self.ack = flag & ACK_FLAG
        self.fin = flag & FIN_FLAG

    def get_flag_bytes(self) -> bytes:
        return struct.pack("B", self.syn | self.ack | self.fin)

    def get_flag(self) -> int:
        return self.syn | self.ack | self.fin
    
    def set_syn(self):
        self.syn = SYN_FLAG
    
    def set_ack(self):
        self.ack = ACK_FLAG

    def set_fin(self):
        self.fin = FIN_FLAG    