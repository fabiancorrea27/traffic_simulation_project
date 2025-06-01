import itertools
import math
import random
from config import *

import networkx as nx

from simulation.pedestrian import Pedestrian
from simulation.pedestrian_light import PedestrianLight
from util.traffic_utils import TrafficUtils
from .vehicle import Vehicle
from .traffic_light import TrafficLight
from .exceptions import CollisionErrorException


class Intersection:
    def __init__(self):
        self.traffic_lights = {
            "N": TrafficLight("N"),
            "S": TrafficLight("S"),
            "E": TrafficLight("E"),
            "W": TrafficLight("W"),
        }
        self.__configure_lights_time()
        self.__configure_first_light()
        self.vehicles = {
            "N": [],
            "S": [],
            "E": [],
            "W": [],
        }
        self.pedestrians = []
        self.pedestrians_light = {
            "N": [PedestrianLight("ES"), PedestrianLight("WS")],
            "S": [PedestrianLight("EN"), PedestrianLight("WN")],
            "E": [PedestrianLight("SW"), PedestrianLight("NW")],
            "W": [PedestrianLight("NE"), PedestrianLight("SE")],
        }
        self.simulation_view = None

    def __configure_lights_time(self):
        for l in self.traffic_lights.values():
            if l.direction == "N":
                l.red_time = config["RED_LIGHT_TIME"]
                l.green_time = DEFAULT_GREEN_NORTH_LIGHT_TIME
            elif l.direction == "S":
                l.red_time = config["RED_LIGHT_TIME"]
                l.green_time = DEFAULT_GREEN_SOUTH_LIGHT_TIME
            elif l.direction == "E":
                l.red_time = config["RED_LIGHT_TIME"]
                l.green_time = DEFAULT_GREEN_EAST_LIGHT_TIME
            elif l.direction == "W":
                l.red_time = config["RED_LIGHT_TIME"]
                l.green_time = DEFAULT_GREEN_WEST_LIGHT_TIME

    def __configure_first_light(self):
        lights_order = TRAFFIC_LIGHTS_ORDER
        self.traffic_lights[lights_order[1]].state = GREEN

    def add_vehicle(self, direction):
        self.vehicles[direction].append(Vehicle(direction))

    def add_vehicle(self, vehicle):
        self.vehicles[vehicle.initial_direction].append(vehicle)
        vehicle.calculate_turning_limit()

    def add_vehicles(self, amount, direction):
        for _ in range(amount):
            vehicle = Vehicle(direction, direction)
            vehicle.change_random_final_direction()
            self.__change_vehicle_random_asset(vehicle)
            vehicle.calculate_size()
            vehicle.calculate_initial_position()
            vehicle.calculate_turning_limit()
            self.vehicles[direction].append(vehicle)

        self.__locate_vehicles_by_direction(direction)

    def __change_vehicle_random_asset(self, vehicle):
        vehicle.asset = random.choice(
            self.simulation_view.vehicles_assets[vehicle.initial_direction]
        )

    def __locate_vehicles_by_direction(self, direction):
        offset = 0
        for vehicle in self.vehicles[direction]:
            random_spacing = random.randint(0, 30)
            total_spacing = VEHICLE_SPACING + random_spacing
            if vehicle.initial_direction == "N":
                total_spacing += vehicle.height
                vehicle.y += offset
                vehicle.initial_offset = offset
                offset += total_spacing
            elif vehicle.initial_direction == "S":
                total_spacing += vehicle.height
                vehicle.y -= offset
                vehicle.initial_offset = offset
                offset += total_spacing
            elif vehicle.initial_direction == "E":
                total_spacing += vehicle.width
                vehicle.x -= offset
                vehicle.initial_offset = offset
                offset += total_spacing
            elif vehicle.initial_direction == "W":
                total_spacing += vehicle.width
                vehicle.x += offset
                vehicle.initial_offset = offset
                offset += total_spacing

    def add_pedestrians(self, amount):
        for _ in range(amount):
            pedestrian = Pedestrian()
            pedestrian.graph = TrafficUtils.pedestrian_graph()
            pedestrian.change_random_initial_direction()
            pedestrian.change_random_final_direction()
            pedestrian.calculate_initial_position()
            self.pedestrians.append(pedestrian)

    def add_pedestrian(self, initial_direction, final_direction):
        pedestrian = Pedestrian()
        pedestrian.graph = TrafficUtils.pedestrian_graph()
        pedestrian.initial_direction = initial_direction
        pedestrian.final_direction = final_direction
        pedestrian.calculate_change_points()
        pedestrian.calculate_initial_position()
        self.pedestrians.append(pedestrian)

    def update(self):
        vehicle_list = [v for sublist in self.vehicles.values() for v in sublist]

        for v1, v2 in itertools.combinations(vehicle_list, 2):
            self.__control_vehicles_crash(v1, v2)

        for v in vehicle_list:
            self.__control_light_car_stop_action(v)
            v.speed = 0 if v.is_stopped else VEHICLE_SPEED
            self.__count_lights_passing_vehicles(v)
            self.__control_vehicle_out_of_bounds(v)
            v.update()
            v.is_stopped = False

        for p in self.pedestrians:
            self.__control_light_pedestrian_stop_action(p)
            self.__control_pedestrian_out_limit(p)
            p.speed = 0 if p.is_stopped else PEDESTRIAN_SPEED
            p.update()
            p.is_stopped = False

    def __control_light_car_stop_action(self, vehicle):
        light = self.traffic_lights[vehicle.initial_direction]
        if light.state in (YELLOW, RED) and self.__verify_vehicle_nearby_light(
            vehicle, light
        ):
            vehicle.is_stopped = True

    def __verify_vehicle_nearby_light(self, vehicle, light):
        if light.direction == "N":
            return (
                abs(vehicle.y - light.position[1] + LIGHT_RADIUS * 2) < LIGHT_LIMIT
            ) and (vehicle.y > light.position[1])
        elif light.direction == "S":
            return (
                abs(vehicle.y + vehicle.height - light.position[1]) < LIGHT_LIMIT
            ) and (vehicle.y < light.position[1])
        elif light.direction == "E":
            return (
                abs(vehicle.x + vehicle.width - light.position[0]) < LIGHT_LIMIT
            ) and (vehicle.x < light.position[0])
        elif light.direction == "W":
            return (
                abs(vehicle.x - light.position[0] + LIGHT_RADIUS * 2) < LIGHT_LIMIT
            ) and (vehicle.x > light.position[0])

    def __control_vehicles_crash(self, vehicle1, vehicle2):
        if (vehicle1.is_turning or vehicle2.is_turning) and (
            vehicle1.initial_direction != vehicle2.initial_direction
        ):
            if self.__vehicle_will_collide_while_turning(vehicle1, vehicle2):
                return
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
        return distance < config["VEHICLE_WIDTH"]

    def __vehicle_will_collide_same_direction(self, vehicle1, vehicle2):
        if vehicle1.initial_direction != vehicle2.initial_direction:
            return False

        same_lane = False
        distance = 0

        if vehicle1.initial_direction in ("N", "S"):
            same_lane = abs(vehicle1.x - vehicle2.x) < vehicle1.width
            if vehicle1.y > vehicle2.y:
                distance = vehicle1.y - (vehicle2.y + vehicle2.height)
            else:
                distance = vehicle2.y - (vehicle1.y + vehicle1.height)

        elif vehicle1.initial_direction in ("E", "W"):
            same_lane = abs(vehicle1.y - vehicle2.y) < vehicle1.height
            if vehicle1.x < vehicle2.x:
                distance = vehicle2.x - (vehicle1.x + vehicle1.width)
            else:
                distance = vehicle1.x - (vehicle2.x + vehicle2.width)

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
            (vehicle.final_direction == "N" and vehicle.y < -vehicle.height)
            or (vehicle.final_direction == "S" and vehicle.y > config["WINDOW_HEIGHT"])
            or (
                vehicle.final_direction == "E"
                and vehicle.x > config["SIMULATION_WIDTH"]
            )
            or (vehicle.final_direction == "W" and vehicle.x < -vehicle.width)
        ):
            vehicle.reset_to_initial_state(True)

    def __count_lights_passing_vehicles(self, vehicle):
        for light in self.traffic_lights.values():
            if light.direction == vehicle.initial_direction and not vehicle.has_counted:
                if light.direction == "N" and vehicle.y < light.position[1]:
                    light.passing_vehicles += 1
                    vehicle.has_counted = True
                elif (
                    light.direction == "S"
                    and vehicle.y + vehicle.height > light.position[1]
                ):
                    light.passing_vehicles += 1
                    vehicle.has_counted = True
                elif (
                    light.direction == "E"
                    and vehicle.x + vehicle.width > light.position[0]
                ):
                    light.passing_vehicles += 1
                    vehicle.has_counted = True
                elif light.direction == "W" and vehicle.x < light.position[0]:
                    light.passing_vehicles += 1
                    vehicle.has_counted = True

    def __control_pedestrian_out_limit(self, pedestrian):
        center_limits = TrafficUtils.calculate_center_limits()
        road_half = config["ROAD_WIDTH"] // 2
        if pedestrian.has_moved and (
            (
                pedestrian.final_direction in ("NE", "NW")
                and pedestrian.y >= center_limits["bottom"] + road_half
            )
            or (
                pedestrian.final_direction in ("SE", "SW")
                and pedestrian.y <= center_limits["top"] - road_half
            )
            or (
                pedestrian.final_direction in ("EN", "ES")
                and pedestrian.x <= center_limits["left"] - road_half
            )
            or (
                pedestrian.final_direction in ("WN", "WS")
                and pedestrian.x >= center_limits["right"] + road_half
            )
        ):
            pedestrian.reset_to_initial_state(True)

    def __control_light_pedestrian_stop_action(self, pedestrian):
        central_limits = TrafficUtils.calculate_center_limits()
        if (
            pedestrian.direction_movement == "N"
            and pedestrian.y >= central_limits["bottom"]
        ):
            if (
                pedestrian.actual_direction == "BL"
                and self.traffic_lights["E"].state == GREEN
            ):
                pedestrian.is_stopped = True
            elif (
                pedestrian.actual_direction == "BR"
                and self.traffic_lights["W"].state == GREEN
            ):
                pedestrian.is_stopped = True
        elif (
            pedestrian.direction_movement == "S"
            and pedestrian.y <= central_limits["top"]
        ):
            if (
                pedestrian.actual_direction == "TL"
                and self.traffic_lights["E"].state == GREEN
            ):
                pedestrian.is_stopped = True
            elif (
                pedestrian.actual_direction == "TR"
                and self.traffic_lights["W"].state == GREEN
            ):
                pedestrian.is_stopped = True
        elif (
            pedestrian.direction_movement == "E"
            and pedestrian.x <= central_limits["left"]
        ):
            if (
                pedestrian.actual_direction == "TL"
                and self.traffic_lights["S"].state == GREEN
            ):
                pedestrian.is_stopped = True
            elif (
                pedestrian.actual_direction == "BL"
                and self.traffic_lights["N"].state == GREEN
            ):
                pedestrian.is_stopped = True
        elif (
            pedestrian.direction_movement == "W"
            and pedestrian.x >= central_limits["right"]
        ):
            if (
                pedestrian.actual_direction == "TR"
                and self.traffic_lights["S"].state == GREEN
            ):
                pedestrian.is_stopped = True
            elif (
                pedestrian.actual_direction == "BR"
                and self.traffic_lights["N"].state == GREEN
            ):
                pedestrian.is_stopped = True

    def check_lights_state(self, toggle_timer):
        lights_order = TRAFFIC_LIGHTS_ORDER
        for i in lights_order.keys():
            if self.__change_light_state(lights_order[i], toggle_timer):
                return
            else:
                if (
                    i == len(lights_order)
                    and self.traffic_lights[lights_order[i]].was_green
                ):
                    self.__restart_lights_condition()

    def __change_light_state(self, direction, toggle_timer):
        yellow_time = YELLOW_LIGHT_TIME
        light = self.traffic_lights[direction]

        if toggle_timer <= 0:
            return False

        if light.state == YELLOW:
            if toggle_timer % yellow_time == 0:
                if light.last_state == RED:
                    light.state = GREEN 
                    self.__change_pedestrian_light_state(light.direction, RED)
                else:
                    light.state = RED
                    self.__change_pedestrian_light_state(light.direction, GREEN)
                
            return True

        if light.state == RED and not light.was_green:
            light.last_state = light.state
            light.state = YELLOW
            return True

        if light.state == GREEN and toggle_timer % light.green_time == 0:
            light.last_state = light.state
            light.state = YELLOW
            light.was_green = True
            return True

        return False if light.state != GREEN else True

    def __restart_lights_condition(self):
        for light in self.traffic_lights.values():
            light.was_green = False
            light.passing_vehicles = 0

    def __change_pedestrian_light_state(self, direction, state):
        for pedestrian_light in self.pedestrians_light[direction]:
            pedestrian_light.state = state
        
    def change_light_times(self, light_direction, green_time):
        light = self.traffic_lights[light_direction]
        light.green_time = green_time

    def restart_to_initial_state(self):
        for key in self.vehicles.keys():
            for vehicle in self.vehicles[key]:
                vehicle.restart_to_initial_state()

        for key in self.traffic_lights.keys():
            self.traffic_lights[key].was_green = False

        for pedestrian in self.pedestrians:
            pedestrian.restart_to_initial_state()

        for light in self.traffic_lights.values():
            light.was_green = False
            light.state = RED
        self.__configure_first_light()

    def traffic_lights_list(self):
        return [t for t in self.traffic_lights.values()]

    def pedestrian_lights_list(self):
        return [t for light_list in self.pedestrians_light.copy().values() for t in light_list]
    
    def vehicles_list(self):
        return [
            v for vehicle_list in self.vehicles.copy().values() for v in vehicle_list
        ]

    def passing_vehicles_dict(self):
        passing_vehicles_dict = {"N": 0, "S": 0, "E": 0, "W": 0}

        for light in self.traffic_lights.values():
            passing_vehicles_dict[light.direction] = light.passing_vehicles

        return passing_vehicles_dict
