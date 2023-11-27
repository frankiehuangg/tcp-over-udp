import sys
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

    def __wait_syn_req(self):
        print(f'[!] [Handshake] Waiting for SYN request...')

        while True:
            self.connection.socket.settimeout(BLOCKING)
            syn_message = self.connection.listen()

            ip = syn_message.ip
            port = syn_message.port
            segment = syn_message.segment

            if segment == Segment.syn(0):
                print(f'[!] [Handshake] Received SYN response from {ip}:{port}')
                break
            else:
                print(f'[X] [Handshake] Unknown segment received')

    def __send_syn_ack(self):
        syn_ack_message = MessageInfo(
            ip=self.connection.ip,
            port=self.connection.port,
            segment=Segment.syn_ack()
        )

        print()
        print(f'[!] [Handshake] Sending SYN ACK request to {self.server_ip}:{self.server_port}')

        self.connection.send(self.server_ip, self.server_port, syn_ack_message)

        while True:
            try:
                print(f'[!] [Handshake] Waiting for response...')

                self.connection.socket.settimeout(TIMEOUT)
                ack_message = self.connection.listen()

                ip = ack_message.ip
                port = ack_message.port
                segment = ack_message.segment

                if segment == Segment.ack(0, 0):
                    print(f'[!] [Handshake] Received ACK response from {ip}:{port}')
                    break
                else:
                    print(f'[!] [Handshake] Unknown segment received')
                    print(f'[!] [Handshake] Retransmit SYN ACK request to {self.server_ip}:{self.server_port}')

            except TimeoutError as e:
                print(f'[X] [Handshake] Timeout error: {e}')
                print(f'[!] [Handshake] Retransmit SYN ACK request to {self.server_ip}:{self.server_port}')

                self.connection.send(self.server_ip, self.server_port, syn_ack_message)

            except InvalidChecksumError as e:
                print(f'[X] [Handshake] Checksum error: {e}')
                print(f'[!] [Handshake] Retransmit SYN ACK request to {self.server_ip}:{self.server_port}')

                self.connection.send(self.server_ip, self.server_port, syn_ack_message)

    ## to implement: frank
    def __receive_data(self):
        data = b''

        seq_num = 0
        while True:
            try:
                self.connection.socket.settimeout(BLOCKING)
                message = self.connection.listen()

                ip = message.ip
                port = message.port
                segment = message.segment

                if segment == Segment.fin():
                    print(f'[!] Received FIN request from {ip}:{port}')

                    fin_ack_message = MessageInfo(
                        ip=self.connection.ip,
                        port=self.connection.port,
                        segment=Segment.fin_ack()
                    )

                    self.connection.send(self.server_ip, self.server_port, fin_ack_message)

                    print(f'[!] Sending FIN ACK response to {self.server_ip}:{self.server_port}')

                    break

                if segment.seq_num == seq_num:
                    data += segment.payload
                    print(f'[!] Received segment number {seq_num}')

                    ack_message = MessageInfo(
                        ip=self.connection.ip,
                        port=self.connection.port,
                        segment=Segment.ack(seq_num, seq_num)
                    )

                    print(f'[!] Sending ACK response {seq_num} to {self.server_ip}:{self.server_port}')
                    self.connection.send(self.server_ip, self.server_port, ack_message)
                    seq_num += 1

                else:
                    print(f'[X] Rejected segment number {segment.seq_num}')

            except InvalidChecksumError as e:
                print(f'[X] Checksum error: {e}')

        with open(self.output_path, 'wb') as f:
            f.write(data)

        self.connection.socket.close()


def main():
    client_port = int(sys.argv[1])
    broadcast_port = int(sys.argv[2])
    output_path = sys.argv[3]

    client = Client(
        server_ip="localhost",
        server_port=broadcast_port,
        output_path=output_path,
        ip="localhost",
        port=client_port
    )

    client.run()


main()
