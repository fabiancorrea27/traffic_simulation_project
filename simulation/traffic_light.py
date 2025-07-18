from config import RED, config, GREEN

class TrafficLight:
    def __init__(self, direction, initial_state = RED):
        self.direction = direction
        self.position = self.__calculate_position()
        self.state = initial_state
        self.was_green = False
        self.last_state = GREEN
        self.green_time = 0
        self.passing_vehicles = 0
        

    def __calculate_position(self):
        center = config["SIMULATION_CENTER"]
        if self.direction == "E":
            position = (center[0] - config["ROAD_WIDTH"] // 2, center[1] + config["ROAD_WIDTH"] // 4)
        elif self.direction == "W":
            position = (center[0] + config["ROAD_WIDTH"] // 2, center[1] - config["ROAD_WIDTH"] // 4)
        elif self.direction == "S":
            position = (center[0] - config["ROAD_WIDTH"] // 4, center[1] - config["ROAD_WIDTH"] // 2)
        elif self.direction == "N":
            position = (center[0] + config["ROAD_WIDTH"] // 4, center[1] + config["ROAD_WIDTH"] // 2)
        return position
        
   
