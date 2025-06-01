import math
import pygame
from config import *


class SimulationView:
    def __init__(self, screen):
        self.screen = screen

    def draw(
        self,
        traffic_lights_list,
        vehicles_list,
        pedestrians_list,
        pedestrian_lights_list,
    ):
        self.screen.fill(WHITE)

        center = config["SIMULATION_CENTER"]
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
                LIGHT_RADIUS,
            )

        for pedestrian_light in pedestrian_lights_list:
            size_half = pedestrian_light.size // 2
            pygame.draw.polygon(
                self.screen,
                pedestrian_light.state,
                [
                    (pedestrian_light.position[0] + size_half, pedestrian_light.position[1]),
                    (
                        pedestrian_light.position[0] + pedestrian_light.size,
                        pedestrian_light.position[1] + pedestrian_light.size,
                    ),
                    (pedestrian_light.position[0], pedestrian_light.position[1] + pedestrian_light.size),
                ],
            )

        for vehicle in vehicles_list:
            vehicle_turn_angle_limits = vehicle.turn_angle_limits()
            rectangle = pygame.Rect(
                vehicle.x,
                vehicle.y,
                vehicle.width,
                vehicle.height,
            )
            angle = (
                math.degrees(vehicle.turn_angle - vehicle_turn_angle_limits[0])
                * -vehicle_turn_angle_limits[2]
            )
            rotated_asset = vehicle.asset
            if vehicle.is_turning:
                rotated_asset = pygame.transform.rotate(rotated_asset, angle)
            elif vehicle.has_turned and not vehicle.changed_asset:
                angle = (
                    math.degrees(
                        abs(vehicle_turn_angle_limits[1] - vehicle_turn_angle_limits[0])
                    )
                    * -vehicle_turn_angle_limits[2]
                )
                rotated_asset = pygame.transform.rotate(vehicle.asset, angle)
                vehicle.asset = rotated_asset
                vehicle.calculate_size()
                vehicle.adjust_position_after_turn()
                vehicle.changed_asset = True
            self.screen.blit(rotated_asset, rectangle.topleft)

        for pedestrian in pedestrians_list:
            pygame.draw.rect(
                self.screen,
                BLUE,
                (
                    pedestrian.x,
                    pedestrian.y,
                    pedestrian.width,
                    pedestrian.height,
                ),
            )
