import pygame
import pygame_gui
from pygame_gui.elements import UIPanel

from config import config


class ButtonsPanel(UIPanel):
    def __init__(
        self, relative_rect, starting_height, manager, margins=None, container=None, object_id=None
    ):
        super().__init__(
            relative_rect=relative_rect,
            starting_height=starting_height,
            manager=manager,
            margins=margins,
            container=container,
            object_id=object_id,
        )
        self.width = self.get_relative_rect().width
        self.height = self.get_relative_rect().height
        self.final_height = self.get_relative_rect().height
        self.btn_start = self.btn_stop = self.btn_optimize = None
        self.__config_buttons()

    def __config_buttons(self):
        buttons_height = (config["FORM_WIDTH"] // 4) - (
            config["UI_ELEMENTS_SPACING"] * 6
        )
        btn_relative_rect = pygame.Rect(
            (
                config["UI_ELEMENTS_SPACING"],
                config["UI_ELEMENTS_SPACING"],
            ),
            (buttons_height * 3, buttons_height),
        )

        buttons_pos_spacing = btn_relative_rect.width + config["UI_ELEMENTS_SPACING"]

        self.btn_start = pygame_gui.elements.UIButton(
            relative_rect=btn_relative_rect,
            text="Iniciar",
            manager=self.ui_manager,
            container=self,
        )

        btn_relative_rect.x = btn_relative_rect.x + buttons_pos_spacing

        self.btn_stop = pygame_gui.elements.UIButton(
            relative_rect=btn_relative_rect,
            text="Detener",
            manager=self.ui_manager,
            container=self,
        )


        # Botón Optimizar (debajo de los otros dos botones)
        btn_relative_rect.x = config["UI_ELEMENTS_SPACING"]  # Reiniciar posición X
        btn_relative_rect.y = btn_relative_rect.y + btn_relative_rect.height + config["UI_ELEMENTS_SPACING"]  # Nueva fila

        self.btn_optimize = pygame_gui.elements.UIButton(
            relative_rect=btn_relative_rect,
            text="Optimizar",
            manager=self.ui_manager,
            container=self,
        )

        # Calcular la altura final del panel
        self.final_height = btn_relative_rect.y + btn_relative_rect.height + config["UI_ELEMENTS_SPACING"]
    
    
    def adjust_height(self):
        self.set_dimensions((self.relative_rect.width, self.final_height))

