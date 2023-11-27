from dataclasses import dataclass

from lib.connection import Node, Connection
from lib.segment import Segment


@dataclass
class Server(Node):
    data: bytes
    input_path: str

    def __init__(self, input_path: str, ip: str = "localhost", port: int = 8000):
        super().__init__()

        self.connection = Connection(ip=ip, port=port)
        print(f'[!] Server started at {self.connection.ip}:{self.connection.port}')

        with open(input_path, 'rb') as f:
            self.data = f.read()

        print(f'[!] Source file | {input_path} | {len(self.data)} bytes')

    def run(self):
        pass

