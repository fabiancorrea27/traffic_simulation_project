import pygame

from config import ROAD_WIDTH, WINDOW_HEIGHT, WINDOW_WIDTH, GREEN, VEHICLE_SIZE, VEHICLE_SPEED, YELLOW


class Vehicle:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.speed = VEHICLE_SPEED
        self.direction = direction  # 'N', 'S', 'E', 'W'
        self.size = VEHICLE_SIZE

    def __init__(self, direction):
        self.direction = direction  # 'N', 'S', 'E', 'W'
        position = self.__calculate_position()
        self.x = position[0]
        self.y = position[1]
        self.speed = VEHICLE_SPEED
        self.size = VEHICLE_SIZE

    def __calculate_position(self):
        center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        if self.direction == "E":
            position = (-VEHICLE_SIZE, center[1] + VEHICLE_SIZE * 2)
        elif self.direction == "W":
            position = (WINDOW_WIDTH, center[1] - VEHICLE_SIZE * 2)
        elif self.direction == "N":
            position = (center[0] + VEHICLE_SIZE * 2, WINDOW_HEIGHT)
        elif self.direction == "S":
            position = (center[0] - VEHICLE_SIZE * 2, -VEHICLE_SIZE)
        return position

    def update(self, traffic_light):
        if (traffic_light.state == GREEN) or (traffic_light.state == YELLOW):
            if self.direction == "S":
                self.y += self.speed
            elif self.direction == "N":
                self.y -= self.speed
            elif self.direction == "E":
                self.x += self.speed
            elif self.direction == "W":
                self.x -= self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 255, 255), (self.x, self.y, self.size, self.size))
