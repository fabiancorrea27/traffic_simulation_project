from config import config, GREEN

class TrafficLight:
    def __init__(self, direction, initial_state = GREEN):
        self.direction = direction
        self.position = self.__calculate_position()
        self.state = initial_state
        self.last_state = None
        self.red_time = 10
        self.green_time = 10
        

    def __calculate_position(self):
        center = (config["SIMULATION_WIDTH"] // 2, config["WINDOW_HEIGHT"] // 2)
        if self.direction == "E":
            position = (center[0] - config["ROAD_WIDTH"] // 2, center[1] + config["ROAD_WIDTH"] // 4)
        elif self.direction == "W":
            position = (center[0] + config["ROAD_WIDTH"] // 2, center[1] - config["ROAD_WIDTH"] // 4)
        elif self.direction == "S":
            position = (center[0] - config["ROAD_WIDTH"] // 4, center[1] - config["ROAD_WIDTH"] // 2)
        elif self.direction == "N":
            position = (center[0] + config["ROAD_WIDTH"] // 4, center[1] + config["ROAD_WIDTH"] // 2)
        return position
        
   
