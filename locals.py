""" toutes les variables globales"""

from typing import Final
import pygame
import ctypes

FLAG_COMAND: Final = "f"
CLICK_COMAND: Final = "c"
GET_NB_FLAGS_COMAND: Final = "g"
GET_NB_BLANKS_COMAND: Final = "b"

UNUSEFUL_COMAND: Final = "u"
NEW_BOX_COMAND: Final = "n"
DID_SOMETHING: Final = "s"
NEW_BOX_DEL_COMAND: Final = "d"

FLAG_DISC_BLANK: Final = 0
FLAG_DISC_DISC: Final = 1
FLAG_DISC_FLAG: Final = -1
FLAG_DISC_MINE: Final = -2
FLAG_DISC_WRONG_FLAG: Final = -3
FLAG_DISC_WRONG_CLICK: Final = -4

BLANK_CASE: Final = "□"
FLAG: Final = "▴"
MINE: Final = "Ω"
WRONG_FLAG: Final = "X"
WRONG_CLICK: Final = "■"
FLAG_DISC_CONV: Final = {
    FLAG_DISC_BLANK: BLANK_CASE,
    FLAG_DISC_FLAG: FLAG,
    FLAG_DISC_MINE: MINE,
    FLAG_DISC_WRONG_FLAG: WRONG_FLAG,
    FLAG_DISC_WRONG_CLICK: WRONG_CLICK
}

SCREEN_SIZE = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)

BUTTON_HEIGHT = (SCREEN_SIZE[1] - 200) // 5  # pour avoir la hauteur de l'écran
BUTTON_TEXT_SIZE = BUTTON_HEIGHT // 4
BUTTON_TEXT_COLOR = 0, 0, 0

DIFFICULTES = {"1": ((9, 9), 10),
               "2": ((16, 16), 40),
               "3": ((30, 16), 99),
               "4": ((50, 50), 500),
               "5": ((100, 100), 2000)}
