import pygame
from config import *


class SimulationView:
    def __init__(self, screen):
        self.screen = screen

    def draw(
        self,
        traffic_lights_list,
        vehicles_list,
    ):
        self.screen.fill(WHITE)

        center = (config["SIMULATION_WIDTH"] // 2, config["WINDOW_HEIGHT"] // 2)
        pygame.draw.rect(
            self.screen,
            GRAY,
            (
                center[0] - config["ROAD_WIDTH"] // 2,
                0,
                config["ROAD_WIDTH"],
                config["WINDOW_HEIGHT"],
            ),
        )
        pygame.draw.rect(
            self.screen,
            GRAY,
            (
                0,
                center[1] - config["ROAD_WIDTH"] // 2,
                config["SIMULATION_WIDTH"],
                config["ROAD_WIDTH"],
            ),
        )

        for traffic_light in traffic_lights_list:
            pygame.draw.circle(
                self.screen,
                traffic_light.state,
                traffic_light.position,
                config["LIGHT_RADIUS"],
            )

        for vehicle in vehicles_list:
            pygame.draw.rect(
                self.screen,
                (0, 255, 255),
                (vehicle.x, vehicle.y, vehicle.size, vehicle.size),
                0,
                1,
            )
            
        
