import math
import pygame

from config import (
    ROAD_WIDTH,
    TURNING_SPEED,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    GREEN,
    VEHICLE_SIZE,
    VEHICLE_SPEED,
    YELLOW,
)


class Vehicle:
    def __init__(self, x, y, initial_direction):
        self.x = x
        self.y = y
        self.speed = VEHICLE_SPEED
        self.initial_direction = initial_direction  # 'N', 'S', 'E', 'W'
        self.final_direction = initial_direction
        self.size = VEHICLE_SIZE
        self.stopped = False

    def __init__(self, initial_direction):
        self.initial_direction = initial_direction  # 'N', 'S', 'E', 'W'
        position = self.__calculate_position()
        self.x = position[0]
        self.y = position[1]
        self.speed = VEHICLE_SPEED
        self.size = VEHICLE_SIZE
        self.stopped = False

    def __init__(self, initial_direction, final_direction):
        self.initial_direction = initial_direction  # 'N', 'S', 'E', 'W'
        self.final_direction = final_direction
        position = self.__calculate_position()
        self.x = position[0]
        self.y = position[1]
        self.turning_limit = self.__calculate_turning_limit()
        self.speed = VEHICLE_SPEED
        self.size = VEHICLE_SIZE
        self.stopped = False
        self.turning = False
        self.turn_angle = 0

    def __calculate_position(self):
        center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        if self.initial_direction == "E":
            position = (-VEHICLE_SIZE, center[1] + ROAD_WIDTH // 4 - VEHICLE_SIZE // 2)
        elif self.initial_direction == "W":
            position = (WINDOW_WIDTH, center[1] - ROAD_WIDTH // 4 - VEHICLE_SIZE // 2)
        elif self.initial_direction == "N":
            position = (center[0] + ROAD_WIDTH // 4 - VEHICLE_SIZE // 2, WINDOW_HEIGHT)
        elif self.initial_direction == "S":
            position = (center[0] - ROAD_WIDTH // 4 - VEHICLE_SIZE // 2, -VEHICLE_SIZE)
        return position

    def __calculate_turning_limit(self):
        top, bottom, left, right = self.__calculate_center_limits()

        limit_map = {
            ("N", "E"): (self.x, WINDOW_HEIGHT // 2),
            ("N", "W"): (self.x, top),
            ("S", "E"): (self.x, bottom),
            ("S", "W"): (self.x, WINDOW_HEIGHT // 2),
            ("E", "N"): (WINDOW_WIDTH // 2, self.y),
            ("E", "S"): (left, self.y),
            ("W", "N"): (right, self.y),
            ("W", "S"): (WINDOW_WIDTH // 2, self.y),
        }

        x_limit, y_limit = limit_map.get(
            (self.initial_direction, self.final_direction), (None, None)
        )

        return x_limit, y_limit

    def __calculate_circle_turn_center(self):
        center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        limit_map = {
            ("N", "E"): (
                WINDOW_WIDTH // 2 + ROAD_WIDTH // 2,
                WINDOW_HEIGHT // 2 - ROAD_WIDTH // 2,
            ),
            ("N", "W"): (center[0], center[1]),
            ("S", "E"): (center[0], center[1]),
            ("S", "W"): (
                WINDOW_WIDTH // 2 - ROAD_WIDTH // 2,
                WINDOW_HEIGHT // 2 + ROAD_WIDTH // 2,
            ),
            ("E", "S"): (center[0], center[1]),
            ("E", "N"): (
                WINDOW_WIDTH // 2 - ROAD_WIDTH // 2,
                WINDOW_HEIGHT // 2 + ROAD_WIDTH // 2,
            ),
            ("W", "S"): (center[0], center[1]),
            ("W", "N"): (
                WINDOW_WIDTH // 2 + ROAD_WIDTH // 2,
                WINDOW_HEIGHT // 2 - ROAD_WIDTH // 2,
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
            if abs(self.x - x_limit) == 0 and abs(self.y - y_limit) == 0:
                self.turning = True
                self.turn_angle = self.__turn_angle_limits()[0]
        self.__move()

    def __move(self):
        if self.turning:
            self.turn_angle += TURNING_SPEED  # velocidad del giro
            if self.turn_angle > self.__turn_angle_limits()[1]:
                self.turn_angle = self.__turn_angle_limits()[1]
                self.turning = False
                self.x = round(self.x)
                self.y = round(self.y)
                self.initial_direction = self.final_direction
            else:
                self.__choose_turning_calculation()
        else:
            # movimiento normal en línea recta
            self.__update_straight()

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

    def __choose_turning_calculation(self):
        radius = ROAD_WIDTH // 4
        x_center, y_center = self.__calculate_circle_turn_center()
        angle_direction = self.__turn_angle_limits()[2]
        self.x = x_center + radius * math.cos(self.turn_angle * angle_direction)
        self.y = y_center + radius * math.sin(self.turn_angle * angle_direction)

    def __update_straight(self):
        if self.initial_direction == "S":
            self.y += self.speed
        elif self.initial_direction == "N":
            self.y -= self.speed
        elif self.initial_direction == "E":
            self.x += self.speed
        elif self.initial_direction == "W":
            self.x -= self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 255, 255), (self.x, self.y, self.size, self.size))
