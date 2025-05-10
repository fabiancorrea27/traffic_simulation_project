import math
import pygame

from config import (
    ROAD_WIDTH,
    TURNING_SPEED,
    VEHICLE_SPACING,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    GREEN,
    VEHICLE_SIZE,
    VEHICLE_SPEED,
    YELLOW,
)


class Vehicle:
    def __init__(self, initial_direction, final_direction):
        self.initial_direction = initial_direction  # 'N', 'S', 'E', 'W'
        self.final_direction = final_direction
        self.x = 0
        self.y = 0
        self.turn_angle = 0
        self.speed = VEHICLE_SPEED
        self.size = VEHICLE_SIZE
        self.has_stopped = False
        self.turning = False
        self.has_turned = False
        self.has_moved = False
        self.turning_limit = (None, None)
        self.calculate_initial_position()

    def calculate_initial_position(self):
        center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        position = (0, 0)
        if self.initial_direction == "E":
            position = (-VEHICLE_SIZE, center[1] + ROAD_WIDTH // 4 - VEHICLE_SIZE // 2)
        elif self.initial_direction == "W":
            position = (WINDOW_WIDTH, center[1] - ROAD_WIDTH // 4 - VEHICLE_SIZE // 2)
        elif self.initial_direction == "N":
            position = (center[0] + ROAD_WIDTH // 4 - VEHICLE_SIZE // 2, WINDOW_HEIGHT)
        elif self.initial_direction == "S":
            position = (center[0] - ROAD_WIDTH // 4 - VEHICLE_SIZE // 2, -VEHICLE_SIZE)
        self.x = position[0]
        self.y = position[1]

    def calculate_turning_limit(self):
        top, bottom, left, right = self.__calculate_center_limits()
        center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

        limit_map = {
            ("N", "E"): (center[0] + ROAD_WIDTH // 4, bottom),
            ("N", "W"): (center[0] + ROAD_WIDTH // 4, center[1]),
            ("S", "E"): (center[0] - ROAD_WIDTH // 4, center[1]),
            ("S", "W"): (center[0] - ROAD_WIDTH // 4, top),
            ("E", "N"): (center[0], center[1] + ROAD_WIDTH // 4 - VEHICLE_SIZE // 2),
            ("E", "S"): (left, center[1] + ROAD_WIDTH // 4 - VEHICLE_SIZE // 2),
            ("W", "N"): (right, center[1] - ROAD_WIDTH // 4 - VEHICLE_SIZE // 2),
            ("W", "S"): (center[0], center[1] - ROAD_WIDTH // 4 - VEHICLE_SIZE // 2),
        }

        x_limit, y_limit = limit_map.get(
            (self.initial_direction, self.final_direction), (None, None)
        )

        self.turning_limit = (x_limit, y_limit)

    def __calculate_circle_turn_center(self):
        center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        half_road = ROAD_WIDTH // 2
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

    def __calculate_center_limits(self):
        top_limit = WINDOW_HEIGHT // 2 - ROAD_WIDTH // 2
        bottom_limit = WINDOW_HEIGHT // 2 + ROAD_WIDTH // 2
        left_limit = WINDOW_WIDTH // 2 - ROAD_WIDTH // 2
        right_limit = WINDOW_WIDTH // 2 + ROAD_WIDTH // 2
        return top_limit, bottom_limit, left_limit, right_limit

    def update(self):
        x_limit, y_limit = self.turning_limit
        if not self.turning_limit.__contains__(None):
            if (
                abs(self.x - x_limit) < VEHICLE_SPACING
                and abs(self.y - y_limit) < VEHICLE_SPACING
                and not self.turning
            ):
                self.turning = True
                self.turn_angle = self.__turn_angle_limits()[0]
        self.__move()
        self.__verify_movement()

    def __move(self):
        if self.turning:
            self.turn_angle += TURNING_SPEED  # velocidad del giro
            if self.turn_angle > self.__turn_angle_limits()[1]:
                self.turn_angle = self.__turn_angle_limits()[1]
                self.turning = False
                self.x = round(self.x)
                self.y = round(self.y)
                self.__adjust_position_after_turn()
                self.has_turned = True
                self.turn_angle = 0
            else:
                self.__turn_vehicle()
        else:
            # movimiento normal en línea recta
            self.__move_straight()

    def __turn_angle_limits(self):
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
            (self.initial_direction, self.final_direction), (1, 1, 1)
        )

        return start_angle, end_angle, angle_direction

    def __turn_vehicle(self):
        radius = ROAD_WIDTH // 4
        x_center, y_center = self.__calculate_circle_turn_center()
        angle_direction = self.__turn_angle_limits()[2]
        self.x = x_center + radius * math.cos(self.turn_angle * angle_direction)
        self.y = y_center + radius * math.sin(self.turn_angle * angle_direction)

    def __adjust_position_after_turn(self):
        center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        if self.final_direction == "N":
            self.x = center[0] + ROAD_WIDTH // 4 - VEHICLE_SIZE // 2
        elif self.final_direction == "S":
            self.x = center[0] - ROAD_WIDTH // 4 - VEHICLE_SIZE // 2
        elif self.final_direction == "E":
            self.y = center[1] + ROAD_WIDTH // 4 - VEHICLE_SIZE // 2
        elif self.final_direction == "W":
            self.y = center[1] - ROAD_WIDTH // 4 - VEHICLE_SIZE // 2

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
            or (self.initial_direction == "N" and self.y < WINDOW_HEIGHT)
            or (self.initial_direction == "E" and self.x > 0)
            or (self.initial_direction == "W" and self.x < WINDOW_WIDTH)
        ):
            self.has_moved = True

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 255, 255), (self.x, self.y, self.size, self.size))
        pygame.draw.circle(screen, YELLOW, (self.x, self.y), 2)
