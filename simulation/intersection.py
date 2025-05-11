import itertools
import math
import random
from config import *

from .vehicle import Vehicle
from .traffic_light import TrafficLight
from .exceptions import CollisionErrorException


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

    def add_vehicle(self, direction):
        self.vehicles[direction].append(Vehicle(direction))

    def add_vehicle(self, vehicle):
        self.vehicles[vehicle.initial_direction].append(vehicle)
        vehicle.calculate_turning_limit()

    def add_vehicles(self, amount, direction):
        offset = 0  # Controla la acumulación de la posición
        for _ in range(amount):
            vehicle = Vehicle(direction, direction)
            self.__change_vehicle_random_final_direction(vehicle)
            vehicle.calculate_turning_limit()
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

    def __change_vehicle_random_final_direction(self, vehicle):
        if vehicle.initial_direction == "N":
            vehicle.final_direction = random.choice(["N", "E", "W"])
        elif vehicle.initial_direction == "S":
            vehicle.final_direction = random.choice(["S", "E", "W"])
        elif vehicle.initial_direction == "E":
            vehicle.final_direction = random.choice(["E", "N", "S"])
        elif vehicle.initial_direction == "W":
            vehicle.final_direction = random.choice(["W", "N", "S"])

    def update(self):
        vehicle_list = [v for sublist in self.vehicles.values() for v in sublist]

        for v in vehicle_list:
            self.__control_light_car_stop_action(v)

        for v1, v2 in itertools.combinations(vehicle_list, 2):
            self.__control_vehicles_crash(v1, v2)

        for v in vehicle_list:
            v.speed = 0 if v.is_stopped else VEHICLE_SPEED
            self.__control_vehicle_out_of_bounds(v)
            v.update()
            v.is_stopped = False

    # If a light is yellow or red, stop the vehicle
    def __control_light_car_stop_action(self, vehicle):
        light = self.traffic_lights[vehicle.initial_direction]
        if light.state in (YELLOW, RED) and self.__verify_vehicle_nearby_light(
            vehicle, light
        ):
            vehicle.is_stopped = True

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
        if (vehicle1.is_turning or vehicle2.is_turning) and (
            vehicle1.initial_direction != vehicle2.initial_direction
        ):
            if self.__vehicle_will_collide_while_turning(vehicle1, vehicle2):
                raise CollisionErrorException()
        else:
            if self.__vehicle_will_collide_same_direction(vehicle1, vehicle2):
                if self.__is_behind(vehicle1, vehicle2):
                    vehicle1.is_stopped = True
                else:
                    vehicle2.is_stopped = True

    def __vehicle_will_collide_while_turning(self, vehicle1, vehicle2):
        dx = vehicle1.x - vehicle2.x
        dy = vehicle1.y - vehicle2.y
        distance = math.hypot(dx, dy)
        return distance < VEHICLE_SIZE

    def __vehicle_will_collide_same_direction(self, vehicle1, vehicle2):
        if vehicle1.initial_direction != vehicle2.initial_direction:
            return False

        same_lane = False
        distance = 0

        if vehicle1.initial_direction in ("N", "S"):
            same_lane = abs(vehicle1.x - vehicle2.x) < vehicle1.size
            if vehicle1.y > vehicle2.y:
                distance = vehicle1.y - (vehicle2.y + vehicle2.size)
            else:
                distance = vehicle2.y - (vehicle1.y + vehicle1.size)

        elif vehicle1.initial_direction in ("E", "W"):
            same_lane = abs(vehicle1.y - vehicle2.y) < vehicle1.size
            if vehicle1.x < vehicle2.x:
                distance = vehicle2.x - (vehicle1.x + vehicle1.size)
            else:
                distance = vehicle1.x - (vehicle2.x + vehicle2.size)

        return same_lane and abs(distance) <= VEHICLE_SPACING

    def __is_behind(self, rear, front):
        if rear.has_turned or front.has_turned:
            return self.__is_behind_with_different_direction(rear, front)
        else:
            return self.__is_behind_with_same_direction(rear, front)

    def __is_behind_with_different_direction(self, rear, front):
        if rear.final_direction == "N":
            return rear.y > front.y
        elif rear.final_direction == "S":
            return rear.y < front.y
        elif rear.final_direction == "E":
            return rear.x < front.x
        elif rear.final_direction == "W":
            return rear.x > front.x

        return False

    def __is_behind_with_same_direction(self, rear, front):
        if rear.initial_direction == "N":
            return rear.y > front.y
        elif rear.initial_direction == "S":
            return rear.y < front.y
        elif rear.initial_direction == "E":
            return rear.x < front.x
        elif rear.initial_direction == "W":
            return rear.x > front.x

        return False

    def __control_vehicle_out_of_bounds(self, vehicle):
        if vehicle.has_moved and (
            (vehicle.final_direction == "N" and vehicle.y < -VEHICLE_SIZE)
            or (vehicle.final_direction == "S" and vehicle.y > WINDOW_HEIGHT)
            or (vehicle.final_direction == "E" and vehicle.x > WINDOW_WIDTH)
            or (vehicle.final_direction == "W" and vehicle.x < -VEHICLE_SIZE)
        ):
            self.__rearrange_vehicle(vehicle)

    def __rearrange_vehicle(self, vehicle):
        self.__change_vehicle_random_final_direction(vehicle)
        vehicle.calculate_turning_limit()
        vehicle.calculate_initial_position()
        vehicle.has_moved = False
        vehicle.has_turned = False

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
        for v in (
            v for vehicle_list in self.vehicles.copy().values() for v in vehicle_list
        ):
            v.draw(screen)
