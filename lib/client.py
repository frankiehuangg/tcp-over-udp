from lib.node import Node


class Client(Node):
    def __init__(self, connection):
        super().__init__(connection)
        
        self._server_ip = None
        self._server_port = None

    def set_server_ip(self, server_ip: str):
        self._server_ip = server_ip

    def set_server_port(self, server_port: int):
        self._server_port = server_port

    def get_server_ip(self) -> str:
        return self._server_ip
    
    def get_server_port(self) -> int:
        return self._server_port
    
    def run(self):
        pass

    def handle_message(self, segment):
        pass
    
