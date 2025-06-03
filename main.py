import pygame
from config import GREEN, RED, config
from ui import MainView
from simulation.intersection import Intersection
from simulation.TrafficFlowOptimizer import TrafficFlowOptimizer

def main():
    main_view = MainView()
    intersection = Intersection()
    main_view.intersection = intersection
    intersection.simulation_view = main_view
    intersection.add_vehicles(8, "N")
    intersection.add_vehicles(4, "S")
    intersection.add_vehicles(13, "E")
    intersection.add_vehicles(20, "W")
    # intersection.add_pedestrians(15)
    optimizer = TrafficFlowOptimizer(intersection)

    running = True

    toggle_timer = 0
    while running:

        if main_view.is_simulation_running:
            toggle_timer += 1
            intersection.lights_toggle_timer += 1
            intersection.check_lights_state()
            intersection.update()
            if (toggle_timer / 60) == 300:
                main_view.stop_button_event()
                toggle_timer = 0
            
        if main_view.optimize_requested:
            main_view.optimize_requested = False
            optimal_times = optimizer.start_optimization_cycle(time_limit_seconds=300)
            print("Tiempos óptimos:", optimal_times)

        if not main_view.update():
            running = False

    pygame.quit()


if __name__ == "__main__":
    main()
