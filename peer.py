import sys
from dataclasses import dataclass
from math import ceil

from lib.connection import Node, MessageInfo, Connection
from lib.constant import TIMEOUT, PAYLOAD_SIZE, WINDOW_SIZE, MSG_FLAG, BLOCKING
from lib.exception import InvalidChecksumError
from lib.segment import Segment, SegmentFlag


@dataclass
class Peer(Node):
    user_ip: str
    user_port: int
    input_path: str

    remote_ip: str
    remote_port: int
    output_path: str

    user_data: bytes
    remote_data: bytes

    def __init__(
            self,
            user_port: int,
            remote_port: int,
            input_path: str,
            output_path: str,
            user_ip: str = "localhost",
            remote_ip: str = "localhost",
    ):
        self.user_ip = user_ip
        self.user_port = user_port
        self.remote_ip = remote_ip
        self.remote_port = remote_port
        self.input_path = input_path
        self.output_path = output_path

        self.connection = Connection(ip=self.user_ip, port=self.user_port)

        with open(input_path, 'rb') as f:
            self.user_data = f.read()

    def run(self):
        print(f'[!] Initiating request to {self.remote_ip}:{self.remote_port}...')

        is_receiver = self.__three_way_handshake()

        if is_receiver:
            self.__listen_data()

            print(f'[!] Peer now acting as sender')
            self.__send_syn()
            self.__listen_syn_ack()
            self.__send_ack()

            self.__send_data()
            self.__send_fin()
        else:
            self.__send_data()
            self.__send_fin()

            print(f'[!] Peer now acting as receiver')
            self.__listen_syn()
            self.__send_syn_ack()
            self.__listen_ack()

            self.__listen_data()

        self.connection.socket.close()

    def __three_way_handshake(self) -> bool:
        print(f'[!] Starting peer')
        try:
            # listen to SYN, if received then reply with SYN ACK, and listen to ACK
            print(f'[!] Peer now acting as receiver')
            self.__listen_syn()
            self.__send_syn_ack()
            self.__listen_ack()
            return True

        except TimeoutError or InvalidChecksumError as _:
            # if SYN not received, send SYN, listen to SYN ACK, and send ACK
            print(f'[!] Peer now acting as sender')
            self.__send_syn()
            self.__listen_syn_ack()
            self.__send_ack()
            return False

    def __send_syn(self):
        syn_message = MessageInfo(
            ip=self.connection.ip,
            port=self.connection.port,
            segment=Segment.syn(0)
        )

        self.connection.send(self.remote_ip, self.remote_port, syn_message)

        print()
        print(f'[!] [Handshake] Sending SYN request to {self.remote_ip}:{self.remote_port}')

    def __send_syn_ack(self):
        syn_ack_message = MessageInfo(
            ip=self.connection.ip,
            port=self.connection.port,
            segment=Segment.syn_ack()
        )

        self.connection.send(self.remote_ip, self.remote_port, syn_ack_message)

        print()
        print(f'[!] [Handshake] Sending SYN ACK request to {self.remote_ip}:{self.remote_port}')

    def __send_ack(self):
        ack_message = MessageInfo(
            ip=self.connection.ip,
            port=self.connection.port,
            segment=Segment.ack(0, 0)
        )

        self.connection.send(self.remote_ip, self.remote_port, ack_message)

        print()
        print(f'[!] [Handshake] Sending ACK request to {self.remote_ip}:{self.remote_port}')

    def __send_fin(self):
        fin_message = MessageInfo(
            ip=self.connection.ip,
            port=self.connection.port,
            segment=Segment.fin()
        )

        self.connection.send(self.remote_ip, self.remote_port, fin_message)

        print()
        print(f'[!] [Final] Sending FIN ACK response to {self.remote_ip}:{self.remote_port}')

    def __send_fin_ack(self):
        fin_ack_message = MessageInfo(
            ip=self.connection.ip,
            port=self.connection.port,
            segment=Segment.fin_ack()
        )

        self.connection.send(self.remote_ip, self.remote_port, fin_ack_message)

        print()
        print(f'[!] [Final] Sending FIN ACK response to {self.remote_ip}:{self.remote_port}')

    def __listen_syn(self):
        try:
            self.connection.socket.settimeout(TIMEOUT)
            syn_message = self.connection.listen()

            ip = syn_message.ip
            port = syn_message.port
            segment = syn_message.segment

            if segment == Segment.syn(0):
                print(f'[!] [Handshake] Received SYN response from {ip}:{port}')

            else:
                print(f'[X] [Handshake] Unknown segment received')

        except TimeoutError as e:
            print(f'[X] [Handshake] Timeout error: {e}')
            raise TimeoutError()

        except InvalidChecksumError as e:
            print(f'[X] [Handshake] Checksum error: {e}')

    def __listen_syn_ack(self):
        try:
            print(f'[!] [Handshake] Waiting for response...')
            self.connection.socket.settimeout(TIMEOUT)
            syn_ack_message = self.connection.listen()

            ip = syn_ack_message.ip
            port = syn_ack_message.port
            segment = syn_ack_message.segment

            if segment == Segment.syn_ack():
                print(f'[!] [Handshake] Received SYN ACK response from {ip}:{port}')

            else:
                print(f'[!] [Handshake] Unknown segment received')

        except TimeoutError as e:
            print(f'[X] [Handshake] Timeout error: {e}')

        except InvalidChecksumError as e:
            print(f'[X] [Handshake] Checksum error: {e}')

    def __listen_ack(self):
        try:
            print(f'[!] [Handshake] Waiting for response...')

            self.connection.socket.settimeout(TIMEOUT)
            ack_message = self.connection.listen()

            ip = ack_message.ip
            port = ack_message.port
            segment = ack_message.segment

            if segment == Segment.ack(0, 0):
                print(f'[!] [Handshake] Received ACK response from {ip}:{port}')

            else:
                print(f'[!] [Handshake] Unknown segment received')

        except TimeoutError as e:
            print(f'[X] [Handshake] Timeout error: {e}')

        except InvalidChecksumError as e:
            print(f'[X] [Handshake] Checksum error: {e}')

    def __send_data(self):
        client_ip = self.remote_ip
        client_port = self.remote_port

        total_segment = ceil(len(self.user_data) / PAYLOAD_SIZE)
        window_size = min(total_segment, WINDOW_SIZE)

        print(f'total segment: {total_segment}')

        seq_base = 0

        on_transfer = 0
        while seq_base != total_segment:

            while on_transfer < window_size:
                payload = self.user_data[
                          (seq_base + on_transfer) * PAYLOAD_SIZE:(seq_base + on_transfer + 1) * PAYLOAD_SIZE]

                segment = Segment(
                    flags=SegmentFlag(MSG_FLAG),
                    seq_num=seq_base + on_transfer,
                    ack_num=seq_base,
                    checksum=b'',
                    payload=payload
                )

                segment.update_checksum()

                message_info = MessageInfo(
                    ip=self.connection.ip,
                    port=self.connection.port,
                    segment=segment
                )

                self.connection.send(client_ip, client_port, message_info)
                print(f'[!] Sending segment {seq_base + on_transfer} to {client_ip}:{client_port}')

                on_transfer += 1

            self.connection.socket.settimeout(TIMEOUT)
            while True:
                try:
                    ack_message = self.connection.listen()

                    ack_num = ack_message.segment.ack_num

                    print(f'[!] Received ACK response {ack_num} from {client_ip}:{client_port}')

                    if ack_num == seq_base:
                        print(f'[!] ACK received sequentially, sending the next segment')
                        seq_base += 1
                        on_transfer -= 1
                    else:
                        print(
                            f'[X] ACK number does not match, retransmit {window_size} segments starting from {seq_base}')
                        on_transfer = 0

                except TimeoutError as e:
                    on_transfer = 0
                    print(f'[X] Timeout error: {e}')
                    break

    def __listen_data(self):
        self.remote_data = b''

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

                    self.connection.send(self.remote_ip, self.remote_port, fin_ack_message)

                    print(f'[!] Sending FIN ACK response to {self.remote_ip}:{self.remote_port}')

                    break

                if segment.seq_num == seq_num:
                    self.remote_data += segment.payload
                    print(f'[!] Received segment number {seq_num}')

                    ack_message = MessageInfo(
                        ip=self.connection.ip,
                        port=self.connection.port,
                        segment=Segment.ack(seq_num, seq_num)
                    )

                    print(f'[!] Sending ACK response {seq_num} to {self.remote_ip}:{self.remote_port}')
                    self.connection.send(self.remote_ip, self.remote_port, ack_message)
                    seq_num += 1

                elif segment.seq_num < seq_num:
                    ack_message = MessageInfo(
                        ip=self.connection.ip,
                        port=self.connection.port,
                        segment=Segment.ack(segment.seq_num, segment.seq_num)
                    )

                    print(f'[!] Resending ACK response {segment.seq_num} to {self.remote_ip}:{self.remote_port}')
                    self.connection.send(self.remote_ip, self.remote_port, ack_message)

                else:
                    print(f'[X] Rejected segment number {segment.seq_num}')

            except TimeoutError as e:
                print(f'[X] Timeout error: {e}')

            except InvalidChecksumError as e:
                print(f'[X] Checksum error: {e}')

        with open(self.output_path, 'wb') as f:
            f.write(self.remote_data)


def main():
    user_port = int(sys.argv[1])
    remote_port = int(sys.argv[2])
    input_path = sys.argv[3]
    output_path = sys.argv[4]

    peer = Peer(
        user_port=user_port,
        remote_port=remote_port,
        input_path=input_path,
        output_path=output_path
    )

    peer.run()


main()
