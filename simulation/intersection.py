import itertools
from config import *

from .vehicle import Vehicle
from .traffic_light import TrafficLight


class Intersection:
    def __init__(self):
        # Semáforos por dirección
        self.traffic_lights = {
            "N": TrafficLight("N"),
            "S": TrafficLight("S"),
            "E": TrafficLight("E"),
            "W": TrafficLight("W"),
        }

        # Vehículos entrando desde el norte
        self.vehicles = {
            "N": [],
            "S": [],
            "E": [],
            "W": [],
        }

    def add_vehicle(self, vehicle):
        self.vehicles[vehicle.direction].append(vehicle)

    def update(self):
        vehicle_list = [v for sublist in self.vehicles.values() for v in sublist]

        for v in vehicle_list:
            self.__control_yellow_light_action(v)

        for v1, v2 in itertools.combinations(vehicle_list, 2):
            if self.__control_vehicles_crash(v1, v2):
                break

        for v in vehicle_list:
            v.update(self.traffic_lights[v.direction])

    # If a light is yellow, stop the vehicle
    def __control_yellow_light_action(self, vehicle):
        light = self.traffic_lights[vehicle.direction]
        if light.state == YELLOW:
            if self.__verify_vehicle_nearby_light(vehicle, light):
                vehicle.speed = 0
        else:
            vehicle.speed = VEHICLE_SPEED
        return True

    # Verify is vehicle is near to a light
    def __verify_vehicle_nearby_light(self, vehicle, light):
        if (abs(vehicle.x - light.position[0] + LIGHT_RADIUS) <= VEHICLE_SPACING) and (
            abs(vehicle.y - light.position[1] + LIGHT_RADIUS) <= VEHICLE_SPACING
        ):
            return True
        else:
            return False

    # Controll vehicles crash
    def __control_vehicles_crash(self, vehicle1, vehicle2):
        if self.__verify_vehicle_near_vehicle(vehicle1, vehicle2):
            vehicle1.speed = 0
            return True
        else:
            vehicle1.speed = VEHICLE_SPEED
            return False

    # Verify if vehicle1 is near vehicle2
    def __verify_vehicle_near_vehicle(self, vehicle1, vehicle2):
        left1 = vehicle1.x - VEHICLE_SPACING
        right1 = vehicle1.x + vehicle1.size + VEHICLE_SPACING
        top1 = vehicle1.y - VEHICLE_SPACING
        bottom1 = vehicle1.y + vehicle1.size + VEHICLE_SPACING

        left2 = vehicle2.x
        right2 = vehicle2.x + vehicle2.size
        top2 = vehicle2.y
        bottom2 = vehicle2.y + vehicle2.size

        horizontal_colision = left1 < right2 and right1 > left2
        vertical_colision = top1 < bottom2 and bottom1 > top2

        return horizontal_colision and vertical_colision

    def change_lights(self):
        light = self.traffic_lights["N"]

        if light.state in (GREEN, RED):
            self.__change_lights_last_state()
            for dir in self.traffic_lights:
                self.traffic_lights[dir].state = YELLOW
            return
        else:
            if light.last_state == RED:
                self.traffic_lights["N"].state = GREEN
                self.traffic_lights["S"].state = GREEN
                self.traffic_lights["E"].state = RED
                self.traffic_lights["W"].state = RED
            else:
                self.traffic_lights["N"].state = RED
                self.traffic_lights["S"].state = RED
                self.traffic_lights["E"].state = GREEN
                self.traffic_lights["W"].state = GREEN

    def __change_lights_last_state(self):
        for light in self.traffic_lights.values():
            light.last_state = light.state

    def draw(self, screen):
        for v in (v for vehicle_list in self.vehicles.values() for v in vehicle_list):
            if (
                (v.direction == "N" and v.y < -VEHICLE_SIZE)
                or (v.direction == "S" and v.y > WINDOW_HEIGHT)
                or (v.direction == "E" and v.x > WINDOW_WIDTH)
                or (v.direction == "W" and v.x < -VEHICLE_SIZE)
            ):
                self.vehicles[v.direction].remove(v)
            v.draw(screen)
