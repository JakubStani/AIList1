class Node:
    def __init__(self, stop_name, stop_lat, stop_lon):
        self.stop_name = stop_name
        self.stop_lat = stop_lat
        self.stop_lon = stop_lon

    def __str__(self):
        return f'stop name: {self.stop_name}, stop lat: {self.stop_lat}, stop lon: {self.stop_lon}'
    
    def _stop_name(self):
        return self.stop_name
    
    def _stop_lat(self):
        return self.stop_lat
    
    def _stop_lon(self):
        return self.stop_lon