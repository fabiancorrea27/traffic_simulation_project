import os
import pygame
import pygame_gui
from config import config
from .form import Form
from .simulation_view import SimulationView


class MainView:

    def __init__(self):
        self.clock = None
        self.closed = False
        self.__config_screen()
        self.manager = pygame_gui.UIManager(
            (config["WINDOW_WIDTH"], config["WINDOW_HEIGHT"]), "assets/theme.json"
        )
        self.intersection = None
        self.simulation_view = SimulationView(self.screen)
        self.form = Form(self.screen, self.manager)
        self.is_simulation_running = False
        self.toggle_time = 0

    def __config_screen(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        info = pygame.display.Info()
        max_width, max_height = info.current_w, info.current_h
        os.environ["SDL_VIDEO_WINDOW_POS"] = "0, 40"
        config["WINDOW_WIDTH"] = max_width
        config["WINDOW_HEIGHT"] = max_height - 100
        self.screen = pygame.display.set_mode(
            (config["WINDOW_WIDTH"], config["WINDOW_HEIGHT"])
        )
        pygame.display.set_caption("Simulación de Intersección")
        config["SIMULATION_WIDTH"] = 3 * config["WINDOW_WIDTH"] / 4
        config["FORM_WIDTH"] = config["WINDOW_WIDTH"] - config["SIMULATION_WIDTH"]

    def update(self, intersection_pojo):
        if not self.__check_events():
            return False
        if self.is_simulation_running:
            self.simulation_view.draw(
                intersection_pojo.traffic_lights_list(),
                intersection_pojo.vehicles_list(),
            )
        time_delta = self.clock.tick(60) / 1000.0
        self.form.update()
        self.manager.update(time_delta)
        self.manager.draw_ui(self.screen)

        pygame.display.flip()

        return True

    def __check_events(self):
        for event in pygame.event.get():
            self.manager.process_events(event)
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.form.buttons_panel.btn_start:
                    self.__change_lights_time()
                    self.form.disable_start_button()
                    self.form.disable_lights_time_panel_inputs()
                    self.is_simulation_running = True
                if event.ui_element == self.form.buttons_panel.btn_stop:
                    self.form.active_start_button()
                    self.form.active_lights_time_panel_inputs()
                    self.is_simulation_running = False
                    self.intersection.restart_to_initial_state()
            if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                self.form.lights_time_panel.verify_text_entry_values()
        return True

    def __change_lights_time(self):
        for i in ("N", "S", "E", "W"):
            self.intersection.change_light_times(
                i,
                float(self.form.lights_time_panel.elements[i]["entries"][0].get_text()),
            )
