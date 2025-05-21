import pygame
from config import GREEN, RED, config
from ui import MainView
from pojos import IntersectionPojo
from simulation import Intersection, Vehicle
   
def main():
    main_view = MainView()
    intersection = Intersection()
    main_view.intersection = intersection
    intersection_pojo = IntersectionPojo(
        intersection.traffic_lights, intersection.vehicles
    )
    intersection.add_vehicles(23, "N")
    intersection.add_vehicles(23, "S")
    intersection.add_vehicles(23, "E")
    intersection.add_vehicles(23, "W")

    running = True
    is_vehicles_collided = False

    toggle_timer = 0
    while running:
        intersection_pojo.traffic_lights = intersection.traffic_lights
        intersection_pojo.vehicles = intersection.vehicles
        if main_view.is_simulation_running:
            if not is_vehicles_collided:
                toggle_timer += 1
                try:
                    intersection.check_lights_state(toggle_timer / 60)
                    intersection.update()
                except Exception as e:
                    is_vehicles_collided = True
                    print(e)

        if not main_view.update(intersection_pojo):
            running = False

    pygame.quit()


if __name__ == "__main__":
    main()
