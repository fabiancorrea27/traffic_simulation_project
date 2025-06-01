import pygame
import pygame_gui
from pygame_gui.elements import UIPanel
from config import *


class LightTimePanel(UIPanel):
    def __init__(
        self, relative_rect, starting_height, manager, container=None, object_id=None
    ):
        super().__init__(
            relative_rect=relative_rect,
            starting_height=starting_height,
            manager=manager,
            container=container,
            object_id=object_id,
        )

        self.elements = {
            "N": {"labels": [], "entries": []},
            "S": {"labels": [], "entries": []},
            "E": {"labels": [], "entries": []},
            "W": {"labels": [], "entries": []},
            "OTHER": {"labels": [], "entries": []},
        }
        self.width = self.get_relative_rect().width
        self.height = self.get_relative_rect().height
        self.final_height = self.get_relative_rect().height
        self.__init_elements()
        self.__config_txt()

    def __init_elements(self):
        lbl_size = self.width // 2 - (config["UI_ELEMENTS_SPACING"] * 3 / 2)
        txtTime_size = lbl_size // 2 - config["UI_ELEMENTS_SPACING"]

        lbl_relative_rect = pygame.Rect(
            (config["UI_ELEMENTS_SPACING"], config["UI_ELEMENTS_SPACING"]),
            (
                config["FORM_WIDTH"] - config["UI_ELEMENTS_SPACING"],
                txtTime_size // 2,
            ),
        )
        txt_relative_rect = pygame.Rect(
            (config["UI_ELEMENTS_SPACING"], config["UI_ELEMENTS_SPACING"]),
            (
                txtTime_size,
                txtTime_size // 2,
            ),
        )
        self.__init_titles(lbl_relative_rect)
        self.__init_North_South_elements(
            lbl_relative_rect, txt_relative_rect, lbl_size, txtTime_size
        )
        self.__init_East_West_elements(
            lbl_relative_rect, txt_relative_rect, lbl_size, txtTime_size
        )
        self.final_height = (
            txt_relative_rect.y
            + txt_relative_rect.height
            + config["UI_ELEMENTS_SPACING"]
        )

    def __init_titles(self, lbl_relative_rect):
        lbl_time_title1 = pygame_gui.elements.UILabel(
            relative_rect=lbl_relative_rect,
            text="Tiempo en verde de semáforos",
            manager=self.ui_manager,
            container=self,
        )

        self.elements["OTHER"]["labels"].append(lbl_time_title1)

        lbl_relative_rect.y = config["UI_ELEMENTS_SPACING"] + lbl_relative_rect.height

        lbl_time_title2 = pygame_gui.elements.UILabel(
            relative_rect=lbl_relative_rect,
            text="según dirección",
            manager=self.ui_manager,
            container=self,
        )

        self.elements["OTHER"]["labels"].append(lbl_time_title2)

    def __init_North_South_elements(
        self, lbl_relative_rect, txt_relative_rect, lbl_size, txtTime_size
    ):
        lbl_relative_rect.width = lbl_size
        lbl_relative_rect.y = (
            lbl_relative_rect.y
            + config["UI_ELEMENTS_SPACING"]
            + lbl_relative_rect.height
        )

        lbl_relative_rect.width = lbl_size

        lbl_N_light = pygame_gui.elements.UILabel(
            relative_rect=lbl_relative_rect,
            text=f"{NORTH_TITLE}",
            manager=self.ui_manager,
            container=self,
        )

        self.elements["N"]["labels"].append(lbl_N_light)

        lbl_relative_rect.x = (
            lbl_relative_rect.x
            + lbl_relative_rect.width
            + config["UI_ELEMENTS_SPACING"]
        )

        lbl_S_light = pygame_gui.elements.UILabel(
            relative_rect=lbl_relative_rect,
            text=f"{SOUTH_TITLE}",
            manager=self.ui_manager,
            container=self,
        )
        self.elements["S"]["labels"].append(lbl_S_light)

        txt_relative_rect.y = lbl_relative_rect.y + lbl_relative_rect.height
        txt_relative_rect.x = (
            config["UI_ELEMENTS_SPACING"] + lbl_size // 2 - txt_relative_rect.width // 2
        )

        txt_N_green_light = pygame_gui.elements.UITextEntryLine(
            relative_rect=txt_relative_rect,
            manager=self.ui_manager,
            container=self,
        )

        self.elements["N"]["entries"].append(txt_N_green_light)

        txt_relative_rect.x = (
            self.width
            + config["UI_ELEMENTS_SPACING"]
            + lbl_size
            - txt_relative_rect.width
        ) // 2

        txt_S_green_light = pygame_gui.elements.UITextEntryLine(
            relative_rect=txt_relative_rect,
            manager=self.ui_manager,
            container=self,
        )

        self.elements["S"]["entries"].append(txt_S_green_light)

    def __init_East_West_elements(
        self, lbl_relative_rect, txt_relative_rect, lbl_size, txtTime_size
    ):
        lbl_relative_rect.width = lbl_size
        lbl_relative_rect.x = config["UI_ELEMENTS_SPACING"]
        lbl_relative_rect.y = (
            txt_relative_rect.y
            + txt_relative_rect.height
            + config["UI_ELEMENTS_SPACING"]
        )
        lbl_E_light = pygame_gui.elements.UILabel(
            relative_rect=lbl_relative_rect,
            text=f"{EAST_TITLE}",
            manager=self.ui_manager,
            container=self,
        )

        self.elements["E"]["labels"].append(lbl_E_light)

        lbl_relative_rect.x = (
            lbl_relative_rect.x
            + lbl_relative_rect.width
            + config["UI_ELEMENTS_SPACING"]
        )

        lbl_W_light = pygame_gui.elements.UILabel(
            relative_rect=lbl_relative_rect,
            text=f"{WEST_TITLE}",
            manager=self.ui_manager,
            container=self,
        )

        self.elements["W"]["labels"].append(lbl_W_light)

        txt_relative_rect.x = (
            config["UI_ELEMENTS_SPACING"] + lbl_size // 2 - txt_relative_rect.width // 2
        )
        txt_relative_rect.y = lbl_relative_rect.y + lbl_relative_rect.height

        txt_E_green_light = pygame_gui.elements.UITextEntryLine(
            relative_rect=txt_relative_rect,
            manager=self.ui_manager,
            container=self,
        )

        self.elements["E"]["entries"].append(txt_E_green_light)

        txt_relative_rect.x = (
            self.width
            + config["UI_ELEMENTS_SPACING"]
            + lbl_size
            - txt_relative_rect.width
        ) // 2

        txt_W_green_light = pygame_gui.elements.UITextEntryLine(
            relative_rect=txt_relative_rect,
            manager=self.ui_manager,
            container=self,
        )

        self.elements["W"]["entries"].append(txt_W_green_light)

    def __config_txt(self):
        self.elements["N"]["entries"][0].set_text(str(DEFAULT_GREEN_NORTH_LIGHT_TIME))
        self.elements["S"]["entries"][0].set_text(str(DEFAULT_GREEN_SOUTH_LIGHT_TIME))
        self.elements["E"]["entries"][0].set_text(str(DEFAULT_GREEN_EAST_LIGHT_TIME))
        self.elements["W"]["entries"][0].set_text(str(DEFAULT_GREEN_WEST_LIGHT_TIME))

    def verify_text_entry_values(self):
        for key in self.elements.keys():
            for entry in self.elements[key]["entries"]:
                if self.__is_valid_float(entry.get_text()):
                    entry.set_text(entry.get_text())
                else:
                    entry.set_text(entry.get_text()[0:-1])

    def __is_valid_float(self, text: str) -> bool:
        try:
            float(text)
            return True
        except ValueError:
            return False

    def adjust_height(self):
        self.set_dimensions((self.relative_rect.width, self.final_height))
