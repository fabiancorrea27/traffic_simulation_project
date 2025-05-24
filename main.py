import pygame
from config import GREEN, RED, config
from ui import MainView
from simulation import Intersection, Vehicle
   
def main():
    main_view = MainView()
    intersection = Intersection()
    main_view.intersection = intersection
    intersection.simulation_view = main_view
    intersection.add_vehicles(2, "N")
    intersection.add_vehicles(2, "S")
    intersection.add_vehicles(2, "E")
    intersection.add_vehicles(2, "W")

    running = True
    is_vehicles_collided = False

    toggle_timer = 0
    while running:
        if main_view.is_simulation_running:
                toggle_timer += 1
                intersection.check_lights_state(toggle_timer / 60)
                intersection.update()

        if not main_view.update():
            running = False

    pygame.quit()


if __name__ == "__main__":
    main()
