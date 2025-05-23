import math
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
        self.vehicles_assets = {"N": [], "S": [], "E": [], "W": []}
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

    def __charge_vehicles_assets(self):
        file_folder = config["VEHICLES_ASSETS_PATH"]
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
            for i in ("N", "S", "E", "W"):
                if i == "N":
                    self.vehicles_assets[i].append(transformed_image)
                elif i == "S":
                    self.vehicles_assets[i].append(
                        pygame.transform.flip(transformed_image, False, True)
                    )
                elif i == "E":
                    self.vehicles_assets[i].append(
                        pygame.transform.rotate(transformed_image, -90)
                    )
                elif i == "W":
                    self.vehicles_assets[i].append(
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

    def adjust_vehicle_asset(self, vehicle):
        vehicle_turn_angle_limits = vehicle.turn_angle_limits()
        angle = (
            math.degrees(
                abs(vehicle_turn_angle_limits[1] - vehicle_turn_angle_limits[0])
            )
            * vehicle_turn_angle_limits[2]
        )
        vehicle.asset = pygame.transform.rotate(vehicle.asset, angle)
