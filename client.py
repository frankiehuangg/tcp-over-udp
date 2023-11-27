from dataclasses import dataclass

from lib.connection import Node, Connection
from lib.segment import Segment


@dataclass
class Client(Node):
    server_ip: str
    server_port: int
    output_path: str

    def __init__(self, server_ip: str, server_port: int, output_path: str, ip: str = "localhost", port: int = 3000):
        super().__init__()

        self.connection = Connection(ip=ip, port=port)
        print(f'[!] Client started at {self.connection.ip}:{self.connection.port}')

        self.server_ip = server_ip
        self.server_port = server_port
        self.output_path = output_path

    def run(self):
        pass

    def handle_message(self, segment: Segment):
        pass
