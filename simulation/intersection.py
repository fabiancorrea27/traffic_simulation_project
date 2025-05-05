import itertools
import random
import time
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

    def add_vehicles(self, amount, direction):
        offset = 0  # Controla la acumulación de la posición
        for _ in range(amount):
            vehicle = Vehicle(direction)

            # Espacio aleatorio adicional (por ejemplo entre 0 y 30 px)
            random_spacing = random.randint(0, 30)
            total_spacing = VEHICLE_SIZE + VEHICLE_SPACING + random_spacing

            if direction == "N":
                vehicle.y += offset
                offset += total_spacing
            elif direction == "S":
                vehicle.y -= offset
                offset += total_spacing
            elif direction == "E":
                vehicle.x -= offset
                offset += total_spacing
            elif direction == "W":
                vehicle.x += offset
                offset += total_spacing

            self.vehicles[direction].append(vehicle)

    def update(self):
        vehicle_list = [v for sublist in self.vehicles.values() for v in sublist]

        for v in vehicle_list:
            self.__control_light_car_stop_action(v)

        for v1, v2 in itertools.combinations(vehicle_list, 2):
            self.__control_vehicles_crash(v1, v2)

        for v in vehicle_list:
            v.speed = 0 if v.stopped else VEHICLE_SPEED
            v.update(self.traffic_lights[v.direction])
            v.stopped = False

    # If a light is yellow, stop the vehicle
    def __control_light_car_stop_action(self, vehicle):
        light = self.traffic_lights[vehicle.direction]
        if light.state in (YELLOW, RED) and self.__verify_vehicle_nearby_light(vehicle, light):
            vehicle.stopped = True

    # Verify is vehicle is near to a light
    def __verify_vehicle_nearby_light(self, vehicle, light):
        if light.direction == "N":
            return (abs(vehicle.y - light.position[1]) < LIGHT_LIMIT) and (
                vehicle.y > light.position[1]
            )
        elif light.direction == "S":
            return (abs(vehicle.y - light.position[1]) < LIGHT_LIMIT) and (
                vehicle.y < light.position[1]
            )
        elif light.direction == "E":
            return (abs(vehicle.x - light.position[0]) < LIGHT_LIMIT) and (
                vehicle.x < light.position[0]
            )
        elif light.direction == "W":
            return (abs(vehicle.x - light.position[0]) < LIGHT_LIMIT) and (
                vehicle.x > light.position[0]
            )

    # Controll vehicles crash
    def __control_vehicles_crash(self, vehicle1, vehicle2):
        if self.__vehicle_will_collide(vehicle1, vehicle2):
            # Determinar quién está detrás (según dirección)
            if self.__is_behind(vehicle1, vehicle2):
                vehicle1.stopped = True
            else:
                vehicle2.stopped = True

    def __is_behind(self, rear, front):
        if rear.direction != front.direction:
            return False  # No van en la misma dirección

        if rear.direction == "N":
            return rear.y > front.y
        elif rear.direction == "S":
            return rear.y < front.y
        elif rear.direction == "E":
            return rear.x < front.x
        elif rear.direction == "W":
            return rear.x > front.x

        return False

    # Verify if vehicle1 will collide with vehicle2
    def __vehicle_will_collide(self, vehicle1, vehicle2):
        if vehicle1.direction != vehicle2.direction:
            return False

        same_lane = False
        distance = 0

        if vehicle1.direction in ("N", "S"):
            same_lane = abs(vehicle1.x - vehicle2.x) < vehicle1.size
            if vehicle1.y > vehicle2.y:
                distance = vehicle1.y - (vehicle2.y + vehicle2.size)
            else:
                distance = vehicle2.y - (vehicle1.y + vehicle1.size)

        elif vehicle1.direction in ("E", "W"):
            same_lane = abs(vehicle1.y - vehicle2.y) < vehicle1.size
            if vehicle1.x < vehicle2.x:
                distance = vehicle2.x - (vehicle1.x + vehicle1.size)
            else:
                distance = vehicle1.x - (vehicle2.x + vehicle2.size)

        return same_lane and abs(distance) <= VEHICLE_SPACING

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
