from lib.node import Node


class Server(Node):
    def __init__(self, connection):
        super().__init__(connection)

    def run(self):
        pass

    def handle_message(self, segment):
        pass