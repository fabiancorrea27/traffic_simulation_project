from config import ROAD_WIDTH, WINDOW_HEIGHT, WINDOW_WIDTH, RED, GREEN

class TrafficLight:
    def __init__(self, direction):
        self.direction = direction
        self.position = self.__calculate_position()
        self.state = GREEN
        self.last_state = None

    def __calculate_position(self):
        center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        if self.direction == "E":
            position = (center[0] - ROAD_WIDTH // 2, center[1] + ROAD_WIDTH // 4)
        elif self.direction == "W":
            position = (center[0] + ROAD_WIDTH // 2, center[1] - ROAD_WIDTH // 4)
        elif self.direction == "S":
            position = (center[0] - ROAD_WIDTH // 4, center[1] - ROAD_WIDTH // 2)
        elif self.direction == "N":
            position = (center[0] + ROAD_WIDTH // 4, center[1] + ROAD_WIDTH // 2)
        return position
        
   
