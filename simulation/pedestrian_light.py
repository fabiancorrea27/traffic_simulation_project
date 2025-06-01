from logging import config
from config import GREEN, PEDESTRIAN_LIGHT_SIZE, config
from util.traffic_utils import TrafficUtils


class PedestrianLight:
    def __init__(self, direction, initial_state = GREEN):
        self.direction = direction
        self.position = (0, 0)
        self.state = initial_state
        self.size = PEDESTRIAN_LIGHT_SIZE
        self.__calculate_position()

    def __calculate_position(self):
        center = config["SIMULATION_CENTER"]
        center_limits = TrafficUtils.calculate_center_limits()
        if self.direction == "NE":
            self.position = (
                center_limits["right"],
                center_limits["bottom"] - self.size,
            )
        elif self.direction == "NW":
            self.position = (
                center_limits["left"] - self.size,
                center_limits["bottom"] - self.size,
            )
        elif self.direction == "SE":
            self.position = (center_limits["right"], center_limits["top"])
        elif self.direction == "SW":
            self.position = (center_limits["left"] - self.size, center_limits["top"])
        elif self.direction == "EN":
            self.position = (center_limits["left"], center_limits["top"] - self.size)
        elif self.direction == "ES":
            self.position = (center_limits["left"], center_limits["bottom"] + self.size)
        elif self.direction == "WN":
            self.position = (
                center_limits["right"] - self.size,
                center_limits["top"] - self.size,
            )
        elif self.direction == "WS":
            self.position = (
                center_limits["right"] - self.size,
                center_limits["bottom"],
            )
