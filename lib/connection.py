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

@dataclass
class Connection:
    ip: str
    port: int
    socket: socket

    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip, self.port))

    def send(self, ip: str, port: int, message: MessageInfo):
        self.socket.sendto(message.segment.get_bytes(), (ip, port))

    def listen(self) -> MessageInfo:
        try:
            data, addr = self.socket.recvfrom(SEGMENT_SIZE)

            seq_num = struct.unpack('!I', data[0:4])[0]
            ack_num = struct.unpack('!I', data[4:8])[0]
            flags = SegmentFlag(data[8])
            checksum = data[10:12]
            payload = data[12:]

            ip = addr[0]
            port = addr[1]

            segment = Segment(
                flags=flags,
                seq_num=seq_num,
                ack_num=ack_num,
                checksum=checksum,
                payload=payload
            )

            if not segment.is_valid_checksum():
                raise InvalidChecksumError(f'[X] Invalid checksum for sequence number {segment.seq_num}')

            message = MessageInfo(
                ip=ip,
                port=port,
                segment=segment
            )

            return message

        except TimeoutError as e:
            raise e

    def close(self):
        self.socket.close()
