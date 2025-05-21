import itertools
import math
import random
from config import *

from .vehicle import Vehicle
from .traffic_light import TrafficLight
from .exceptions import CollisionErrorException


class Intersection():
    def __init__(self):
        # Semáforos por dirección
        self.traffic_lights = {
            "N": TrafficLight("N", RED),
            "S": TrafficLight("S", RED),
            "E": TrafficLight("E"),
            "W": TrafficLight("W"),
        }
        self.__configure_lights_time()
        # Vehículos entrando desde el norte
        self.vehicles = {
            "N": [],
            "S": [],
            "E": [],
            "W": [],
        }

    def __configure_lights_time(self):
        for l in self.traffic_lights.values():
            if l.direction == "N":
                l.red_time = config["RED_LIGHT_TIME"]
                l.green_time = config["DEFAULT_GREEN_NORTH_LIGHT_TIME"]
            elif l.direction == "S":
                l.red_time = config["RED_LIGHT_TIME"]
                l.green_time = config["DEFAULT_GREEN_SOUTH_LIGHT_TIME"]
            elif l.direction == "E":
                l.red_time = config["RED_LIGHT_TIME"]
                l.green_time = config["DEFAULT_GREEN_EAST_LIGHT_TIME"]
            elif l.direction == "W":
                l.red_time = config["RED_LIGHT_TIME"]
                l.green_time = config["DEFAULT_GREEN_WEST_LIGHT_TIME"]

    def add_vehicle(self, direction):
        self.vehicles[direction].append(Vehicle(direction))

    def add_vehicle(self, vehicle):
        self.vehicles[vehicle.initial_direction].append(vehicle)
        vehicle.calculate_turning_limit()

    def add_vehicles(self, amount, direction):
        offset = 0
        for _ in range(amount):
            vehicle = Vehicle(direction, direction)
            self.__change_vehicle_random_final_direction(vehicle)
            vehicle.calculate_turning_limit()
            random_spacing = random.randint(0, 30)
            total_spacing = (
                config["VEHICLE_SIZE"] + config["VEHICLE_SPACING"] + random_spacing
            )

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
            v.speed = 0 if v.is_stopped else config["VEHICLE_SPEED"]
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
            return (abs(vehicle.y - light.position[1]) < config["LIGHT_LIMIT"]) and (
                vehicle.y > light.position[1]
            )
        elif light.direction == "S":
            return (abs(vehicle.y - light.position[1]) < config["LIGHT_LIMIT"]) and (
                vehicle.y < light.position[1]
            )
        elif light.direction == "E":
            return (abs(vehicle.x - light.position[0]) < config["LIGHT_LIMIT"]) and (
                vehicle.x < light.position[0]
            )
        elif light.direction == "W":
            return (abs(vehicle.x - light.position[0]) < config["LIGHT_LIMIT"]) and (
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
        return distance < config["VEHICLE_SIZE"]

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

        return same_lane and abs(distance) <= config["VEHICLE_SPACING"]

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
            (vehicle.final_direction == "N" and vehicle.y < -config["VEHICLE_SIZE"])
            or (vehicle.final_direction == "S" and vehicle.y > config["WINDOW_HEIGHT"])
            or (
                vehicle.final_direction == "E"
                and vehicle.x > config["SIMULATION_WIDTH"]
            )
            or (vehicle.final_direction == "W" and vehicle.x < -config["VEHICLE_SIZE"])
        ):
            self.__rearrange_vehicle(vehicle)

    def __rearrange_vehicle(self, vehicle):
        self.__change_vehicle_random_final_direction(vehicle)
        vehicle.calculate_turning_limit()
        vehicle.calculate_initial_position()
        vehicle.has_moved = False
        vehicle.has_turned = False

    def check_lights_state(self, toggle_timer):
        lights_order = config["TRAFFIC_LIGHTS_ORDER"]
        for light in self.traffic_lights.values():
            self.__change_light_state(light.direction, toggle_timer)

    def __change_light_state(self, direction, toggle_timer):
        yellow_time = config["YELLOW_LIGHT_TIME"]
        light = self.traffic_lights[direction]
        if toggle_timer > 0:
            if (light.state == YELLOW) and (toggle_timer % yellow_time == 0):
                if light.last_state == RED:
                    light.state = GREEN
                else:
                    light.state = RED
                return True
            else:
                if (light.state == RED) and (toggle_timer % light.red_time == 0):
                    light.last_state = light.state
                    light.state = YELLOW
                    return True
                elif (light.state == GREEN) and (toggle_timer % light.green_time == 0):
                    light.last_state = light.state
                    light.state = YELLOW
                    return True
        return False

    def change_light_times(self, light_direction, green_time):
        light = self.traffic_lights[light_direction]
        light.green_time = green_time
