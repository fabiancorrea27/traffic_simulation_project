import pygame
import pygame_gui
from config import config
from .simulation_view import SimulationView


class MainView:

    def __init__(self):
        self.clock = None
        self.closed = False
        self.__config_screen()
        self.simulation_view = SimulationView(self.screen)

    def __config_screen(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        info = pygame.display.Info()
        max_width, max_height = info.current_w, info.current_h
        config["WINDOW_WIDTH"] = 2 * (max_width / 3)
        config["WINDOW_HEIGHT"] = max_height - 100
        self.manager = pygame_gui.UIManager(
            (config["WINDOW_WIDTH"], config["WINDOW_HEIGHT"])
        )
        self.screen = pygame.display.set_mode(
            (config["WINDOW_WIDTH"], config["WINDOW_HEIGHT"])
        )
        pygame.display.set_caption("Simulación de Intersección")

    def update(self, intersection_pojo):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        self.simulation_view.draw(
            intersection_pojo.traffic_lights_list(),
            intersection_pojo.vehicles_list(),
        )
        pygame.display.flip()
        self.clock.tick(60)
        return True
        
        
