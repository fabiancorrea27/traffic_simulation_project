import random
from config import config
from util import TrafficUtils
import networkx as nx


class Pedestrian:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.initial_direction = None
        self.final_direction = None
        self.actual_direction = None
        self.direction_movement = None
        self.change_points = []
        self.graph = None
        self.speed = config["PEDESTRIAN_SPEED"]
        self.width = config["PEDESTRIAN_SIZE"]
        self.height = config["PEDESTRIAN_SIZE"]
        self.has_moved = False
        self.is_stopped = False

    def calculate_initial_position(self):
        center_x, center_y = config["SIMULATION_CENTER"]
        road_three_halfs = 3 * config["ROAD_WIDTH"] // 2
        road_half = config["ROAD_WIDTH"] // 2
        central_limits = TrafficUtils.calculate_center_limits()

        if self.initial_direction == "NE":
            self.x = central_limits["right"] + 10
            self.y = central_limits["bottom"] + road_three_halfs
        elif self.initial_direction == "SE":
            self.x = central_limits["right"] + 10
            self.y = central_limits["top"] - road_three_halfs - self.height
        elif self.initial_direction == "NW":
            self.x = central_limits["left"] - self.width - 10
            self.y = central_limits["bottom"] + road_three_halfs
        elif self.initial_direction == "SW":
            self.x = central_limits["left"] - self.width - 10
            self.y = central_limits["top"] - road_three_halfs - self.height
        elif self.initial_direction == "EN":
            self.x = central_limits["left"] - road_three_halfs - self.width
            self.y = central_limits["top"] - self.height - 10
        elif self.initial_direction == "WN":
            self.x = central_limits["right"] + road_three_halfs
            self.y = central_limits["top"] - self.height - 10
        elif self.initial_direction == "ES":
            self.x = central_limits["left"] - road_three_halfs - self.width
            self.y = central_limits["bottom"] + 10
        elif self.initial_direction == "WS":
            self.x = central_limits["right"] + road_three_halfs
            self.y = central_limits["bottom"] + 10

    def change_random_final_direction(self):
        self.final_direction = random.choice(
            ["NE", "SE", "NW", "SW", "EN", "WN", "ES", "WS"]
        )
        if self.initial_direction == self.final_direction:
            self.change_random_final_direction()
        else:
            self.calculate_change_points()

    def calculate_change_points(self):
        self.change_points = nx.shortest_path(
            self.graph, self.initial_direction, self.final_direction, weight="weight"
        )
        self.actual_direction = self.change_points[0]
        self.direction_movement = self.graph.get_edge_data(
            self.actual_direction, self.change_points[1]
        )["direction"]

    def change_random_initial_direction(self):
        self.initial_direction = random.choice(
            ["NE", "SE", "NW", "SW", "EN", "WN", "ES", "WS"]
        )
        self.actual_direction = self.initial_direction

    def update(self):
        next_point = self.change_points[
            self.change_points.index(self.actual_direction) + 1
        ]
        if self.__check_change_direction(next_point):
            self.__change_direction(next_point)
        else:
            self.__move()

    def __check_change_direction(self, next_point):
        if self.initial_direction != self.final_direction:
            return self.__check_near_next_position(next_point)

    def __corner_limits(self):
        center_limits = TrafficUtils.calculate_center_limits()
        top = center_limits["top"]
        bottom = center_limits["bottom"]
        left = center_limits["left"]
        right = center_limits["right"]
        corner_limits = {
            "TL": (left - self.width - 10, top - self.height - 10),
            "TR": (right + 10, top - self.height - 10),
            "BL": (left - self.width - 10, bottom + 10),
            "BR": (right + 10, bottom + 10),
        }
        return corner_limits

    def __check_near_next_position(self, change_point):
        change_point_limits = None
        if change_point in ("TL", "TR", "BL", "BR"):
            change_point_limits = self.__corner_limits()[change_point]
        if change_point_limits is not None:
            if self.direction_movement == "N" and self.y <= change_point_limits[1]:
                return True
            elif self.direction_movement == "S" and self.y >= change_point_limits[1]:
                return True
            elif self.direction_movement == "E" and self.x >= change_point_limits[0]:
                return True
            elif self.direction_movement == "W" and self.x <= change_point_limits[0]:
                return True
            else:
                return False
        else:
            return False

    def __change_direction(self, next_point):
        next_next_point = self.change_points[self.change_points.index(next_point) + 1]
        direction = self.graph.get_edge_data(next_point, next_next_point)["direction"]
        self.actual_direction = next_point
        self.direction_movement = direction

    def __move(self):
        if self.direction_movement == "N":
            self.y -= self.speed
            self.has_moved = True
        elif self.direction_movement == "S":
            self.y += self.speed
            self.has_moved = True
        elif self.direction_movement == "E":
            self.x += self.speed
            self.has_moved = True
        elif self.direction_movement == "W":
            self.x -= self.speed
            self.has_moved = True

    def reset_to_initial_state(self, change_direction=False):
        self.calculate_initial_position()
        if change_direction:
            self.change_random_final_direction()
        else:
            self.actual_direction = self.change_points[0]
            self.direction_movement = self.graph.get_edge_data(
                self.actual_direction, self.change_points[1]
            )["direction"]
        self.has_moved = False
