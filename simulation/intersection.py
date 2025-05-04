
from .vehicle import Vehicle
from .traffic_light import TrafficLight

class Intersection:
    def __init__(self):
        # Semáforos por dirección
        self.traffic_lights = {
            'N': TrafficLight('N'),
            'S': TrafficLight('S'),
            'E': TrafficLight('E'),
            'W': TrafficLight('W')
        }

        # Vehículos entrando desde el norte
        self.vehicles = [Vehicle(390, 0, 'S')]

    
        
    def update(self):
        for v in self.vehicles:
            v.update(self.traffic_lights[v.direction])

    def draw(self, screen):
        for v in self.vehicles:
            v.draw(screen)
