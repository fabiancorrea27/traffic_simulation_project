import pygame

from config import GREEN

class Vehicle:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.speed = 2
        self.direction = direction  # 'N', 'S', 'E', 'W'
        self.size = 20

    def update(self, traffic_light):
        if traffic_light.get_state() == GREEN:
            if self.direction == 'S':
                self.y += self.speed
            elif self.direction == 'N':
                self.y -= self.speed
            elif self.direction == 'E':
                self.x += self.speed
            elif self.direction == 'W':
                self.x -= self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 255, 255), (self.x, self.y, self.size, self.size))
