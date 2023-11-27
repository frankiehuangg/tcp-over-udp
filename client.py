from dataclasses import dataclass

from lib.connection import Node, Connection, MessageInfo
from lib.constant import TIMEOUT, BLOCKING
from lib.exception import InvalidChecksumError
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
        print(f'[!] Initiating request to {self.server_ip}:{self.server_port}...')
        self.__three_way_handshake()
        self.__receive_data()
        pass

    def __three_way_handshake(self):
        self.__send_syn()
        self.__wait_syn_req()
        self.__send_syn_ack()

    def handle_message(self, segment: Segment):
        pass

    ## to implement
    def __send_syn(self):
        syn_message = MessageInfo(
            ip=self.connection.ip,
            port=self.connection.port,
            segment=Segment.syn(0)
        )

        print()
        print(f'[!] [Request] Sending SYN request to {self.server_ip}:{self.server_port}')

        self.connection.send(self.server_ip, self.server_port, syn_message)

        while True:
            try:
                print(f'[!] [Request] Waiting for response...')
                self.connection.socket.settimeout(TIMEOUT)
                ack_message = self.connection.listen()

                ip = ack_message.ip
                port = ack_message.port
                segment = ack_message.segment

                if segment == Segment.ack(0, 0):
                    print(f'[!] [Request] Received ACK response from {ip}:{port}')
                    print(f'[!] [Request] Client request successfully added to server ')
                    break
                else:
                    print(f'[X] [Request] Unknown segment received')
                    print(f'[!] [Request] Retransmit SYN request to {self.server_ip}:{self.server_port}')

            except TimeoutError as e:
                print(f'[X] [Request] Timeout error: {e}')
                print(f'[!] [Request] Retransmit SYN request to {self.server_ip}:{self.server_port}')

                self.connection.send(self.server_ip, self.server_port, syn_message)

            except InvalidChecksumError as e:
                print(f'[X] [Request] Checksum error: {e}')
                print(f'[!] [Request] Retransmit SYN request to {self.server_ip}:{self.server_port}')

                self.connection.send(self.server_ip, self.server_port, syn_message)

        print()

    ## to implement: kiki
    def __wait_syn_req(self):
        pass
    # to implement: chow
    def __send_syn_ack(self):
        pass
    ## to implement: frank
    def __receive_data(self):
        pass
