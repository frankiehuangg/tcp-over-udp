from dataclasses import dataclass
import struct

from lib.constant import SYN_FLAG, ACK_FLAG, FIN_FLAG, MSG_FLAG


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


@dataclass
class Segment:
    flags: SegmentFlag
    seq_num: int
    ack_num: int
    checksum: bytes
    payload: bytes

    @staticmethod
    def syn(seq_num: int) -> "Segment":
        segment = Segment(
            flags=SegmentFlag(SYN_FLAG),
            seq_num=seq_num,
            ack_num=0,
            checksum=b'',
            payload=b''
        )

        segment.update_checksum()

        return segment

    @staticmethod
    def ack(seq_num: int, ack_num: int) -> "Segment":
        segment = Segment(
            flags=SegmentFlag(ACK_FLAG),
            seq_num=seq_num,
            ack_num=ack_num,
            checksum=b'',
            payload=b''
        )

        segment.update_checksum()

        return segment

    @staticmethod
    def syn_ack() -> "Segment":
        segment = Segment(
            flags=SegmentFlag(SYN_FLAG | ACK_FLAG),
            seq_num=0,
            ack_num=0,
            checksum=b'',
            payload=b''
        )

        segment.update_checksum()

        return segment

    @staticmethod
    def fin() -> "Segment":
        segment = Segment(
            flags=SegmentFlag(FIN_FLAG),
            seq_num=0,
            ack_num=0,
            checksum=b'',
            payload=b''
        )

        segment.update_checksum()

        return segment

    @staticmethod
    def fin_ack() -> "Segment":
        segment = Segment(
            flags=SegmentFlag(FIN_FLAG | ACK_FLAG),
            seq_num=0,
            ack_num=0,
            checksum=b'',
            payload=b''
        )

        segment.update_checksum()

        return segment

    @staticmethod
    def metadata(file_name, file_ext) -> "Segment":
        padded_file_name = file_name.ljust(256, '\x00')
        padded_ext_name = file_ext.ljust(4, '\x00')
        payload = struct.pack("256s4s", padded_file_name.encode(), padded_ext_name.encode())
        segment = Segment(
            flags=SegmentFlag(MSG_FLAG),
            seq_num=0,
            ack_num=0,
            checksum=b'',
            payload=payload
        )

        segment.update_checksum()

        return segment

    def get_bytes(self):
        data = struct.pack('!I', self.seq_num)
        data += struct.pack('!I', self.ack_num)
        data += self.flags.get_flag_bytes()
        data += b'\x00'
        data += self.checksum
        data += self.payload

        return data

    def calculate_checksum(self) -> bytes:
        data = struct.pack('!I', self.seq_num)
        data += struct.pack('!I', self.ack_num)
        data += self.flags.get_flag_bytes()
        data += b'\x00\x00\x00'
        data += self.payload

        xor_in = 0x0000
        xor_out = 0x0000
        poly = 0x8005

        reg = xor_in
        for octet in data:
            for i in range(8):
                topbit = reg & 0x8000
                if octet & (0x80 >> i):
                    topbit ^= 0x8000
                reg <<= 1
                if topbit:
                    reg ^= poly
            reg &= 0xFFFF

        checksum = struct.pack('!H', reg ^ xor_out)

        return checksum

    def update_checksum(self):
        self.checksum = self.calculate_checksum()

    def is_valid_checksum(self) -> bool:
        return self.calculate_checksum() == self.checksum