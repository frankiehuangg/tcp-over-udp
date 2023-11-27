from abc import ABC, abstractmethod
from lib.segment import Segment


class Node(ABC):
    def __init__(self, connection):
        self._connection = connection

    def set_connection(self, connection):
        self._connection = connection

    def get_connection(self):
        return self._connection

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def handle_message(self, segment: Segment):
        pass