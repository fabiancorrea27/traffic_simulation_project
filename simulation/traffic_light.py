from config import ROAD_WIDTH, WINDOW_HEIGHT, WINDOW_WIDTH
from config import RED


class TrafficLight:
    def __init__(self, direction):
        self.direction = direction
        self.position = self._calculate_light_position()
        self.state = RED

    def _calculate_light_position(self):
        center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        if self.direction == "E":
            position = (center[0] + ROAD_WIDTH // 2, center[1])
        elif self.direction == "W":
            position = (center[0] - ROAD_WIDTH // 2, center[1])
        elif self.direction == "N":
            position = (center[0], center[1] - ROAD_WIDTH // 2)
        elif self.direction == "S":
            position = (center[0], center[1] + ROAD_WIDTH // 2)
        return position

    def toggle_state(self, color_state):
        self.state = color_state

    def get_state(self):
        return self.state
