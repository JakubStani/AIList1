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
        self.distance = math.sqrt((float(start_node._stop_lat()) - float(end_node._stop_lat()))**2 + (float(start_node._stop_lon()) - float(end_node._stop_lon()))**2)
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
    