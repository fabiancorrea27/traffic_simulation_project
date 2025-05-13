class IntersectionPojo:
    def __init__(self, traffic_lights, vehicles):
        self.traffic_lights = traffic_lights
        self.vehicles = vehicles
        
    def traffic_lights_list(self):
       return [t for t in self.traffic_lights.values()]
   
    def vehicles_list(self):
       return [v for vehicle_list in self.vehicles.copy().values() for v in vehicle_list]
