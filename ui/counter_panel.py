import pygame
import pygame_gui
from pygame_gui.elements import UIPanel
from pygame_gui.core import ObjectID
from config import config


class CounterPanel:
    def __init__(
        self,
        screen,
        manager,
        lights=None,
    ):
        self.screen = screen
        self.manager = manager
        self.lights = lights
        self.elements_with_value = {"N": None, "S": None, "E": None, "W": None}

    def init_elements(self):
        for key in self.lights.keys():
            light = self.lights[key]
            if light.direction == "N":
                initial_pos = (
                    light.position[0] + config["ROAD_WIDTH"] // 4,
                    light.position[1],
                )
                self.__config_labels(initial_pos, light.direction)
            elif light.direction == "S":
                initial_pos = (
                    light.position[0] - config["ROAD_WIDTH"] // 4 - 190,
                    light.position[1] - 30,
                )
                self.__config_labels(initial_pos, light.direction)
            elif light.direction == "E":
                initial_pos = (
                    light.position[0] - 190,
                    light.position[1] + config["ROAD_WIDTH"] // 4,
                )
                self.__config_labels(initial_pos, light.direction)
            elif light.direction == "W":
                initial_pos = (
                    light.position[0],
                    light.position[1] - config["ROAD_WIDTH"] // 4 - 30,
                )
                self.__config_labels(initial_pos, light.direction)

    def __config_labels(self, initial_pos, direction):
        lbl_relative_rect = pygame.Rect(
            (initial_pos[0], initial_pos[1]),
            (80, 30),
        )
        lbl_title = pygame_gui.elements.UILabel(
            relative_rect=lbl_relative_rect,
            text="Pasaron: ",
            manager=self.manager,
            object_id=ObjectID(class_id="@counter_label"),
        )
        lbl_relative_rect = pygame.Rect(
            (lbl_relative_rect.x + lbl_relative_rect.width, lbl_relative_rect.y),
            (30, 30),
        )
        lbl_value = pygame_gui.elements.UILabel(
            relative_rect=lbl_relative_rect,
            text="0",
            manager=self.manager,
            object_id=ObjectID(class_id="@counter_label"),
        )
        self.elements_with_value[direction] = lbl_value
        lbl_relative_rect = pygame.Rect(
            (lbl_relative_rect.x + lbl_relative_rect.width, lbl_relative_rect.y),
            (80, 30),
        )
        lbl_title2 = pygame_gui.elements.UILabel(
            relative_rect=lbl_relative_rect,
            text=" vehiculos",
            manager=self.manager,
            object_id=ObjectID(class_id="@counter_label"),
        )

    def update(self, values_dict):
        self.elements_with_value["N"].set_text(str(values_dict["N"]))
        self.elements_with_value["S"].set_text(str(values_dict["S"]))
        self.elements_with_value["E"].set_text(str(values_dict["E"]))
        self.elements_with_value["W"].set_text(str(values_dict["W"]))