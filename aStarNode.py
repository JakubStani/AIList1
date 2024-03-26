from node import Node

class AStarNode(Node):
    def __init__(self, stop_name, stop_lat, stop_lon, f, h, g=float('inf')):
        super().__init__(stop_name, stop_lat, stop_lon)
        self.g = g
        self.h = h
        self.f = f

    def _f(self):
        return self.f
    
    def _h(self):
        return self.h
    
    def _g(self):
        return self.g
    
    def setF(self, value):
        self.f=value

    def setH(self, value):
        self.h=value

    def setG(self, value):
        self.g=value

    def __str__(self):
        return super().stop_name