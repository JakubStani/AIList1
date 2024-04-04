from datetime import datetime 
import math

#TODO: fix time operations
class Edge:

    def __init__(self, id, company, line, departure_time, arrival_time, start_node, end_node):

        self.id = id
        self.company = company
        self.line = line
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.start_node = start_node
        self.end_node = end_node

        #IMP: zerknąłem na czyjś kod (sprawdziłem, jakich funkcji użył do zamiany stringa na czas i czasu na sekundy)
        self.time_diff = (abs(datetime.strptime(self.arrival_time, '%H:%M:%S') - datetime.strptime(self.departure_time, '%H:%M:%S'))).total_seconds()

        #obliczenie dystansu (w km) od węzła początkowego,
        #do końcowego za pomocą wzoru "Haversine formula" 
        #(źródło: https://www.youtube.com/watch?v=HaGj0DjX8W8)
        lat1 = float(start_node._stop_lat()) * math.pi / 180
        lon1 = float(start_node._stop_lon()) * math.pi / 180
        lat2 = float(end_node._stop_lat()) * math.pi / 180
        lon2 = float(end_node._stop_lon()) * math.pi / 180
        nauticalMileToKilometers=1.852

        self.distance =(3440.1 * math.acos( 
            (math.sin(lat1) * math.sin(lat2)) +
            math.cos(lat1) * math.cos(lat2) *
            math.cos(lon1 - lon2)) *nauticalMileToKilometers)

    def __str__(self):
        return f'id: {self.id}, \
        company: {self.company}, \
        line: {self.line}, \
        departure time: {self.departure_time}, \
        arrival time: {self.arrival_time}, \
        start node: {self.start_node}, \
        end node: {self.end_node}, \
        time diff: {self.time_diff}, \
        distance: {self.distance}'
    
    def _start_node(self):
        return self.start_node
    
    def _end_node(self):
        return self.end_node
    
    def _time_diff(self):
        return self.time_diff
    
    def _distance(self):
        return self.distance
    def _arrival_time(self):
        return self.arrival_time
    
    def _departure_time(self):
        return self.departure_time
    
    def _company(self):
        return self.company
    
    def _line(self):
        return self.line
    
    def _id(self):
        return self.id
    
    