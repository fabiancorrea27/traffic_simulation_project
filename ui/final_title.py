import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from config import config


class FinalTitle:
    def __init__(
        self,
        screen,
        manager,
    ):
        self.screen = screen
        self.manager = manager
        self.lbl_title_tile1 = self.lbl_title_tile2 = None
        self.lbl_title_value = None
        self.__init_elements()

    def __init_elements(self):
        center = config["SIMULATION_CENTER"]
        simulation_width_third = config["SIMULATION_WIDTH"] // 3
        relative_rect = pygame.Rect(0, center[1] - 45, simulation_width_third, 90)

        self.lbl_title1 = pygame_gui.elements.UILabel(
            relative_rect=relative_rect,
            text="Pasaron",
            manager=self.manager,
            object_id=ObjectID(class_id="@title_label"),
        )

        relative_rect.x = relative_rect.x + relative_rect.width
        
        self.lbl_title_value = pygame_gui.elements.UILabel(
            relative_rect=relative_rect,
            text="0",
            manager=self.manager,
            object_id=ObjectID(class_id="@title_label"),
        )
        
        relative_rect.x = relative_rect.x + relative_rect.width
        self.lbl_title2 = pygame_gui.elements.UILabel(
            relative_rect=relative_rect,
            text="vehiculos",
            manager=self.manager,
            object_id=ObjectID(class_id="@title_label"),
        )

        self.hide()
        
    def show(self, value=0):
        self.lbl_title_value.set_text(str(value))
        self.lbl_title1.visible = True
        self.lbl_title2.visible = True
        self.lbl_title_value.visible = True
        
    def hide(self):
        self.lbl_title1.visible = False
        self.lbl_title2.visible = False
        self.lbl_title_value.visible = False