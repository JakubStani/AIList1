from node import Node

class DjkNode(Node):
    def __init__(self, stop_name, stop_lat, stop_lon, d='inf'):
        super().__init__(self, stop_name, stop_lat, stop_lon)
        self.d = d