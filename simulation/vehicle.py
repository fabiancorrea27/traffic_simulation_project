import math
import random
import pygame
from util import TrafficUtils
from config import DEFAULT_TURNING_SPEED, DEFAULT_VEHICLE_SPEED, GREEN, VEHICLE_SPACING, YELLOW, config


class Vehicle:
    def __init__(self, initial_direction, final_direction):
        self.initial_direction = initial_direction
        self.final_direction = final_direction
        self.x = 0
        self.y = 0
        self.initial_offset = 0
        self.turn_angle = 0
        self.speed = DEFAULT_VEHICLE_SPEED
        self.width = config["VEHICLE_WIDTH"]
        self.height = config["VEHICLE_WIDTH"]
        self.is_stopped = False
        self.is_turning = False
        self.has_turned = False
        self.has_moved = False
        self.turning_limit = (None, None)
        self.asset = None
        self.changed_asset = False
        self.has_counted = False

    def calculate_initial_position(self):
        center = config["SIMULATION_CENTER"]
        road_quarter = config["ROAD_WIDTH"] // 4
        if self.initial_direction == "E":
            self.x = -self.width - self.initial_offset
            self.y = center[1] + road_quarter - self.height // 2
        elif self.initial_direction == "W":
            self.x = config["SIMULATION_WIDTH"] + self.initial_offset
            self.y = center[1] - road_quarter - self.height // 2
        elif self.initial_direction == "N":
            self.x = center[0] + road_quarter - self.width // 2
            self.y = config["WINDOW_HEIGHT"] + self.initial_offset
        elif self.initial_direction == "S":
            self.x = center[0] - road_quarter - self.width // 2
            self.y = -self.height - self.initial_offset

    def calculate_turning_limit(self):
        center_limits = TrafficUtils.calculate_center_limits()
        top = center_limits["top"]
        bottom = center_limits["bottom"]
        left = center_limits["left"]
        right = center_limits["right"]
        center = config["SIMULATION_CENTER"]
        road_quarter = config["ROAD_WIDTH"] // 4

        limit_map = {
            ("N", "E"): (center[0] + road_quarter, bottom),
            ("N", "W"): (center[0] + road_quarter, center[1]),
            ("S", "E"): (center[0] - road_quarter, center[1]),
            ("S", "W"): (center[0] - road_quarter, top),
            ("E", "N"): (
                center[0],
                center[1] + road_quarter - self.height // 2,
            ),
            ("E", "S"): (
                left,
                center[1] + road_quarter - self.height // 2,
            ),
            ("W", "N"): (
                right,
                center[1] - road_quarter - self.height // 2,
            ),
            ("W", "S"): (
                center[0],
                center[1] - road_quarter - self.height // 2,
            ),
        }

        x_limit, y_limit = limit_map.get(
            (self.initial_direction, self.final_direction), (None, None)
        )

        self.turning_limit = (x_limit, y_limit)

    def __calculate_circle_turn_center(self):
        center = config["SIMULATION_CENTER"]
        half_road = config["ROAD_WIDTH"] // 2
        limit_map = {
            ("N", "E"): (
                center[0] + half_road,
                center[1] + half_road,
            ),
            ("N", "W"): (center[0], center[1]),
            ("S", "E"): (center[0], center[1]),
            ("S", "W"): (
                center[0] - half_road,
                center[1] - half_road,
            ),
            ("E", "S"): (center[0] - half_road, center[1] + half_road),
            ("E", "N"): (center[0], center[1]),
            ("W", "S"): (center[0], center[1]),
            ("W", "N"): (
                center[0] + half_road,
                center[1] - half_road,
            ),
        }

        x_coor, y_coor = limit_map.get(
            (self.initial_direction, self.final_direction), (0, 0)
        )

        return x_coor, y_coor

    def calculate_size(self):
        self.width = self.asset.get_width()
        self.height = self.asset.get_height()

    def update(self):
        x_limit, y_limit = self.turning_limit
        if not self.turning_limit.__contains__(None):
            if (
                abs(self.x - x_limit) < VEHICLE_SPACING
                and abs(self.y - y_limit) < VEHICLE_SPACING
                and not self.is_turning
            ):
                self.is_turning = True
                self.turn_angle = self.turn_angle_limits()[0]
        self.__move()
        self.__verify_movement()

    def __move(self):
        if self.is_turning:
            self.turn_angle += DEFAULT_TURNING_SPEED if self.speed > 0 else 0
            if self.turn_angle > self.turn_angle_limits()[1]:
                self.turn_angle = self.turn_angle_limits()[1]
                self.is_turning = False
                self.has_turned = True
                self.turn_angle = 0
                self.turning_limit = (None, None)
            else:
                self.__turn_vehicle()
        else:
            self.__move_straight()

    def turn_angle_limits(self):
        turning_map = {
            ("W", "N"): (math.pi / 2, math.pi, 1),
            ("W", "S"): (math.pi / 2, math.pi, -1),
            ("E", "N"): (3 * math.pi / 2, 2 * math.pi, -1),
            ("E", "S"): (3 * math.pi / 2, 2 * math.pi, 1),
            ("N", "W"): (0, math.pi / 2, -1),
            ("N", "E"): (math.pi, 3 * math.pi / 2, 1),
            ("S", "W"): (0, math.pi / 2, 1),
            ("S", "E"): (math.pi, 3 * math.pi / 2, -1),
        }

        start_angle, end_angle, angle_direction = turning_map.get(
            (self.initial_direction, self.final_direction), (0, 0, 1)
        )

        return start_angle, end_angle, angle_direction

    def __turn_vehicle(self):
        radius = config["ROAD_WIDTH"] // 4
        x_center, y_center = self.__calculate_circle_turn_center()
        angle_direction = self.turn_angle_limits()[2]
        self.x = x_center + radius * math.cos(self.turn_angle * angle_direction)
        self.y = y_center + radius * math.sin(self.turn_angle * angle_direction)

    def adjust_position_after_turn(self):
        self.x = round(self.x)
        self.y = round(self.y)
        center = config["SIMULATION_CENTER"]
        road_quarter = config["ROAD_WIDTH"] // 4
        if self.final_direction == "N":
            self.x = center[0] + road_quarter - self.width // 2
        elif self.final_direction == "S":
            self.x = center[0] - road_quarter - self.width // 2
        elif self.final_direction == "E":
            self.y = center[1] + road_quarter - self.height // 2
        elif self.final_direction == "W":
            self.y = center[1] - road_quarter - self.height // 2

    def calculte_position_after_turn(self):
        center = config["SIMULATION_CENTER"]
        road_quarter = config["ROAD_WIDTH"] // 4
        if self.final_direction == "N":
            return (
                center[0] + road_quarter - self.width // 2,
                round(self.y),
            )
        elif self.final_direction == "S":
            return (
                center[0] - road_quarter - self.width // 2,
                round(self.y),
            )
        elif self.final_direction == "E":
            return (
                round(self.x),
                center[1] + road_quarter - self.height // 2,
            )
        elif self.final_direction == "W":
            return (
                round(self.x),
                center[1] - road_quarter - self.height // 2,
            )

    def __move_straight(self):
        if self.has_turned:
            self.__move_final_direction()
        else:
            self.__move_initial_direction()

    def __move_initial_direction(self):
        if self.initial_direction == "S":
            self.y += self.speed
        elif self.initial_direction == "N":
            self.y -= self.speed
        elif self.initial_direction == "E":
            self.x += self.speed
        elif self.initial_direction == "W":
            self.x -= self.speed

    def __move_final_direction(self):
        if self.final_direction == "S":
            self.y += self.speed
        elif self.final_direction == "N":
            self.y -= self.speed
        elif self.final_direction == "E":
            self.x += self.speed
        elif self.final_direction == "W":
            self.x -= self.speed

    def __verify_movement(self):
        if (
            not self.has_moved
            and (self.initial_direction == "S" and self.y > 0)
            or (self.initial_direction == "N" and self.y < config["WINDOW_HEIGHT"])
            or (self.initial_direction == "E" and self.x > 0)
            or (self.initial_direction == "W" and self.x < config["SIMULATION_WIDTH"])
        ):
            self.has_moved = True

    def change_random_final_direction(self):
        if self.initial_direction == "N":
            self.final_direction = random.choice(["N", "E", "W"])
        elif self.initial_direction == "S":
            self.final_direction = random.choice(["S", "E", "W"])
        elif self.initial_direction == "E":
            self.final_direction = random.choice(["E", "N", "S"])
        elif self.initial_direction == "W":
            self.final_direction = random.choice(["W", "N", "S"])

    def reset_to_initial_state(self, change_direction=False):
        turn_angle_limits = self.turn_angle_limits()
        if self.changed_asset:
            angle = (
                math.degrees(abs(turn_angle_limits[1] - turn_angle_limits[0]))
                * turn_angle_limits[2]
            )
            self.asset = pygame.transform.rotate(self.asset, angle)
            self.calculate_size()
        if change_direction:
            self.change_random_final_direction 
        self.calculate_turning_limit()
        self.has_moved = False
        self.has_turned = False
        self.has_counted = False
        self.changed_asset = False
        self.is_turning = False
        self.turn_angle = 0
        self.calculate_initial_position()
