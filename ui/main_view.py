import math
import os
import pygame
import pygame_gui
from config import VEHICLES_ASSETS_PATH, config
from ui.final_title import FinalTitle
from .counters import Counters
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
        self.counters = Counters(self.screen, self.manager)
        self.final_title = FinalTitle(self.screen, self.manager)
        self.is_simulation_running = False
        self.optimize_requested = False  # <- NUEVO: bandera para optimización
        self.toggle_time = 0
        self.vehicles_assets = {"N": [], "S": [], "E": [], "W": []}
        self.framerate = 60
        self.__charge_vehicles_assets()

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
        config["VEHICLE_WIDTH"] = config["ROAD_WIDTH"] // 6
        config["SIMULATION_WIDTH"] = 3 * config["WINDOW_WIDTH"] / 4
        config["FORM_WIDTH"] = config["WINDOW_WIDTH"] - config["SIMULATION_WIDTH"]
        config["SIMULATION_CENTER"] = (
            config["SIMULATION_WIDTH"] // 2,
            config["WINDOW_HEIGHT"] // 2,
        )

    def __charge_vehicles_assets(self):
        file_folder = VEHICLES_ASSETS_PATH
        files = os.listdir(file_folder)
        files = [
            f
            for f in files
            if os.path.isfile(os.path.join(file_folder, f))
            and f.lower().endswith((".webp", ".jpg", ".png"))
        ]
        self.__add_assets(file_folder, files)

    def __add_assets(self, file_folder, files):
        for f in files:
            transformed_image = self.__transform_image_scale(file_folder, f)
            for direction in ("N", "S", "E", "W"):
                if direction == "N":
                    self.vehicles_assets[direction].append(transformed_image)
                elif direction == "S":
                    self.vehicles_assets[direction].append(
                        pygame.transform.flip(transformed_image, False, True)
                    )
                elif direction == "E":
                    self.vehicles_assets[direction].append(
                        pygame.transform.rotate(transformed_image, -90)
                    )
                elif direction == "W":
                    self.vehicles_assets[direction].append(
                        pygame.transform.rotate(transformed_image, 90)
                    )

    def __transform_image_scale(self, file_folder, file):
        image = pygame.image.load(os.path.join(file_folder, file))
        transformed_image = pygame.transform.scale(
            image,
            (
                config["VEHICLE_WIDTH"],
                image.get_height() * config["VEHICLE_WIDTH"] / image.get_width(),
            ),
        )
        return transformed_image

    def update(self):
        if not self.__check_events():
            return False
        if self.is_simulation_running:
            self.simulation_view.draw(
                self.intersection.traffic_lights_list(),
                self.intersection.vehicles_list(),
                self.intersection.pedestrians,
                self.intersection.pedestrian_lights_list(),
            )
            self.counters.update(self.intersection.passing_vehicles_dict())
        time_delta = self.clock.tick(self.framerate) / 1000.0
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
                    self.start_button_event()
                if event.ui_element == self.form.buttons_panel.btn_stop:
                    self.stop_button_event()
                if event.ui_element == self.form.buttons_panel.btn_increase_time:
                    self.increase_time_button_event()
                if event.ui_element == self.form.buttons_panel.btn_optimize:
                    self.optimize_requested = True
            if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                self.form.lights_time_panel.verify_text_entry_values()

        return True

    def start_button_event(self):

        self.final_title.hide()
        self.__change_lights_time()
        self.form.disable_start_button()
        self.form.disable_lights_time_panel_inputs()
        self.counters.lights = self.intersection.traffic_lights
        self.counters.init_elements()
        self.is_simulation_running = True

    def stop_button_event(self):
        self.form.active_start_button()
        self.form.active_lights_time_panel_inputs()
        self.is_simulation_running = False
        self.final_title.show(self.intersection.total_passing_vehicles)
        self.intersection.restart_to_initial_state()

    def increase_time_button_event(self):
        if not self.form.buttons_panel.is_increased_time:
            self.form.buttons_panel.is_increased_time = True
            self.framerate *= 5
        else:
            self.form.buttons_panel.is_increased_time = False
            self.framerate /= 5

    def __change_lights_time(self):
        for i in ("N", "S", "E", "W"):
            self.intersection.change_light_times(
                i,
                float(self.form.lights_time_panel.elements[i]["entries"][0].get_text()),
            )
