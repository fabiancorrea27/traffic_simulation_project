import pygame
from config import GREEN, config
from ui import MainView
from pojos import IntersectionPojo
from simulation import Intersection, Vehicle


def main():
    main_view = MainView()
    intersection = Intersection()
    intersection_pojo = IntersectionPojo(
        intersection.traffic_lights, intersection.vehicles
    )
    intersection.add_vehicles(3, "N")
    intersection.add_vehicles(3, "S")
    intersection.add_vehicles(3, "E")
    intersection.add_vehicles(3, "W")

    running = True
    is_vehicles_collided = False

    toggle_timer = 0

    while running:
        intersection_pojo.traffic_lights = intersection.traffic_lights
        intersection_pojo.vehicles = intersection.vehicles
        toggle_timer += 1
        if toggle_timer >= 120:
            intersection.change_lights()
            toggle_timer = 0
        if not is_vehicles_collided:
            try:
                intersection.update()
            except Exception as e:
                is_vehicles_collided = True
                print(e)

        if not main_view.update(intersection_pojo):
            running = False

    pygame.quit()


if __name__ == "__main__":
    main()
