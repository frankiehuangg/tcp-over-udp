import sys
from dataclasses import dataclass
from math import ceil

from lib.connection import Node, Connection, MessageInfo
from lib.constant import BLOCKING, TIMEOUT, PAYLOAD_SIZE, WINDOW_SIZE, MSG_FLAG
from lib.exception import InvalidChecksumError
from lib.segment import Segment, SegmentFlag


class ListeningClient:
    ip: str
    port: int

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port


@dataclass
class Server(Node):
    data: bytes
    input_path: str
    clients: list[ListeningClient]

    def __init__(self, input_path: str, ip: str = "localhost", port: int = 8000):
        super().__init__()
        self.clients = []
        self.connection = Connection(ip=ip, port=port)
        print(f'[!] Server started at {self.connection.ip}:{self.connection.port}')

        with open(input_path, 'rb') as f:
            self.data = f.read()

        print(f'[!] Source file | {input_path} | {len(self.data)} bytes')

    def run(self):
        print(f'[!] Listening to {self.connection.ip}:{self.connection.port} for clients\n')
        self.__listen_for_clients()
        self.__print_clients()
        self.__start_file_transfer()
        pass

    def __print_clients(self):
        print(f'Client list: ')
        for client in self.clients:
            print(f'- {client.ip}:{client.port}')
        pass

    def __listen_for_clients(self):
        print(f'[!] Listening to {self.connection.ip}:{self.connection.port} for clients\n')

        while True:
            self.connection.socket.settimeout(BLOCKING)
            syn_message = self.connection.listen()

            ip = syn_message.ip
            port = syn_message.port
            segment = syn_message.segment

            if segment == Segment.syn(0):
                self.clients.append(ListeningClient(ip, port))

                print(f'[!] [Request] Received request from {ip}:{port}')

                ack_message = MessageInfo(
                    ip=self.connection.ip,
                    port=self.connection.port,
                    segment=Segment.ack(0, 0)
                )

                self.connection.send(ip, port, ack_message)

                response = input(f'[?] [Request] Listen more? (y/n) ')
                while response not in ['y', 'n']:
                    print(f'[X] [Request] Please choose between (y) and (n)')

                    response = input(f'[?] [Request] Listen more? (y/n) ')

                if response == 'n':
                    break

            else:
                print(f'[X] [Request] Unknown segment received')
        pass

    def __start_file_transfer(self):
        for client in self.clients:
            self.__three_way_handshake(client)
            self.__send_data(client)

    def __three_way_handshake(self, client: ListeningClient):
        print(f'[!] [Handshake] Handshake to client at {client.ip}:{client.port}')

        syn_message = MessageInfo(
            ip=self.connection.ip,
            port=self.connection.port,
            segment=Segment.syn(0)
        )

        print(f'[!] [Handshake] Sending SYN request to {client.ip}:{client.port}')

        self.connection.send(client.ip, client.port, syn_message)

        while True:
            try:
                print(f'[!] [Handshake] Waiting for response...')
                self.connection.socket.settimeout(TIMEOUT)
                syn_ack_message = self.connection.listen()

                ip = syn_ack_message.ip
                port = syn_ack_message.port
                segment = syn_ack_message.segment

                if segment == Segment.syn_ack():
                    print(f'[!] [Handshake] Received SYN ACK response from {ip}:{port}')
                    break
                else:
                    print(f'[!] [Handshake] Unknown segment received')
                    print(f'[!] [Handshake] Retransmit SYN request to {client.ip}:{client.port}')

            except TimeoutError as e:
                print(f'[X] [Handshake] Timeout error: {e}')
                print(f'[!] [Handshake] Retransmit SYN request to {client.ip}:{client.port}')

                self.connection.send(client.ip, client.port, syn_message)

            except InvalidChecksumError as e:
                print(f'[X] [Handshake] Checksum error: {e}')
                print(f'[!] [Handshake] Retransmit SYN request to {client.ip}:{client.port}')

                self.connection.send(client.ip, client.port, syn_message)

        ack_message = MessageInfo(
            ip=self.connection.ip,
            port=self.connection.port,
            segment=Segment.ack(0, 0)
        )

        self.connection.send(client.ip, client.port, ack_message)

        print(f'[!] [Handshake] Sending ACK request to {client.ip}:{client.port}')
        print(f'[!] [Handshake] Handshake completed')
        print()

    ## to implement: frankie
    def __send_data(self, client: ListeningClient):
        print(f'[!] File transfer to {client.ip}:{client.port} completed')
        print()
        self.__send_fin(client)
        pass

    ## to implement: kiki
    def __send_fin(self, client: ListeningClient):
        pass
