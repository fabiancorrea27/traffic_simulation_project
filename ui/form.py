import pygame
import pygame_gui
from pygame_gui.elements import UIPanel
from pygame_gui.core import ObjectID
from config import config
from .buttons_panel import ButtonsPanel
from .lights_time_panel import LightTimePanel


class Form:
    def __init__(self, screen, manager):
        self.screen = screen
        self.manager = manager

        self.main_panel = None
        self.lights_time_panel = None
        self.buttons_panel = None
        self.__init_elements()
        self.update()

    def __init_elements(self):
        panel_rect = pygame.Rect(
            (config["SIMULATION_WIDTH"], 0),
            (config["FORM_WIDTH"], config["WINDOW_HEIGHT"]),
        )
        self.main_panel = UIPanel(
            relative_rect=panel_rect,
            starting_height=1,
            manager=self.manager,
        )
        panel_rect = pygame.Rect(
            (0, 0),
            (config["FORM_WIDTH"], config["WINDOW_HEIGHT"] / 2),
        )
        self.lights_time_panel = LightTimePanel(
            relative_rect=panel_rect,
            starting_height=2,
            manager=self.manager,
            container=self.main_panel,
            object_id=ObjectID(class_id='@sub_panel', object_id='#lights_panel'),
        )
        panel_rect.y = panel_rect.y + panel_rect.height + config["UI_ELEMENTS_SPACING"]
        self.buttons_panel = ButtonsPanel(
            relative_rect=panel_rect,
            starting_height=2,
            manager=self.manager,
            container=self.main_panel,
            object_id=ObjectID(class_id='@sub_panel', object_id='#buttons_panel'),
        )

    def update(self):
        self.lights_time_panel.adjust_height()
        self.buttons_panel.adjust_height()
        self.__adjust_panels()
        

    def __adjust_panels(self):
        self.buttons_panel.set_relative_position(
            (
                0,
                self.lights_time_panel.get_relative_rect().y
                + self.lights_time_panel.get_relative_rect().height
                + config["UI_ELEMENTS_SPACING"],
            )
        )
        
    def disable_lights_time_panel_inputs(self):
        for key in self.lights_time_panel.elements.keys():
            for entry in self.lights_time_panel.elements[key]["entries"]:
                entry.disable()
                
    def active_lights_time_panel_inputs(self):
        for key in self.lights_time_panel.elements.keys():
            for entry in self.lights_time_panel.elements[key]["entries"]:
                entry.enable()
    
    def disable_start_button(self):
        self.buttons_panel.btn_start.disable()
        
    def active_start_button(self):
        self.buttons_panel.btn_start.enable()
