""" fichier contenant la base du démieur"""

import random
import time

from locals import *


class Board:
    """ Classe contenant la base du jeu"""

    def __init__(self, size: tuple[int, int], numb_mines, show_whole=False):
        self._size = size
        self._numb_mines = numb_mines
        self._numb_flags = 0
        self._show_whole = show_whole

        # contient où sont les mines et le nombre de mines autour de chaque case
        self._mines = [[0 for _ in range(size[0])] for _ in range(size[1])]
        # self.numbs = [[0 for _ in range(size[0])] for _ in range(size[1])]  # bug du .copy avec les doubles tableaux

        # toutes les cases qui ont étées découvertes et celles qui sont "flag"
        self.flag_discovered = [[FLAG_DISC_BLANK for _ in range(size[0])] for _ in range(size[1])]

        self._game_started = False
        self.lost = False
        self.game_finished = False

        self.last_modified = []
        self.starting_time = 0

    def __confirm_first_click(self, starting_pos: tuple[int, int]) -> None:
        """ pose toutes les mines au hasard en étant sur de laisser une petite place pour commencer la partie"""

        # cette variable sert à ne pas poser deux mines dans une case
        # Elle sert aussi à laisser une zone de 3x3 autour de la première case cliquée
        all_cords = [
            (i, j) for j in range(self._size[1]) for i in range(self._size[0])
            if not (starting_pos[0] - 1 <= i <= starting_pos[0] + 1 and starting_pos[1] - 1 <= j <= starting_pos[1] + 1)
        ]
        for i in range(self._numb_mines):
            tmp = all_cords.pop(random.randint(0, len(all_cords) - 1))
            self._mines[tmp[1]][tmp[0]] = -1

        # puis on détermine quel nombre devrait avoir toutes les autres cases qui ne sont pas des mines
        all_cords.extend([(i, j) for i in range(starting_pos[0] - 1, starting_pos[0] + 2)
                          for j in range(starting_pos[1] - 1, starting_pos[1] + 2)])
        for i in range(self._size[1]):
            for j in range(self._size[0]):
                if not self.__is_mine((j, i)):
                    self._mines[i][j] = self.__get_numb_mines((j, i))
        self._game_started = True
        self.starting_time = time.time()

    def __is_mine(self, cords: tuple[int, int]) -> bool:
        """ rend True si la case donnée est une mine, False sinon"""
        return self._mines[cords[1]][cords[0]] == -1

    def __get_numbs(self, cords: tuple[int, int]) -> int:
        """ rend la valeur de la case aux coordonées donées"""
        return (lambda x: x if x >= 0 else -1)(self._mines[cords[1]][cords[0]])

    def __get_numb_mines(self, cord: tuple[int, int]) -> int:
        """ rend le nombre de mines autour d'une case"""
        ret = 0
        for i in range(cord[1] - 1, cord[1] + 2):
            for j in range(cord[0] - 1, cord[0] + 2):
                if (j, i) != cord and 0 <= i < self._size[1] and 0 <= j < self._size[0]:
                    ret += self.__is_mine((j, i))
        return ret

    def get_size(self) -> tuple[int, int]:
        """ rend les dimensions du démineur"""
        return self._size

    def has_game_started(self) -> bool:
        """ rend si la partie à commencé"""
        return self._game_started

    def has_lost(self) -> bool:
        """ rend si le jeu est perdu (si on a cliqué sur une mine)"""
        return self.lost

    def has_won(self) -> bool:
        """ rend si le jeu est gagné (toutes les cases qui ne sont pas des mines ont étées découvertes)"""
        for i in range(self._size[1]):
            for j in range(self._size[0]):
                if not self.__is_mine((j, i)) and not self.flag_discovered[i][j] == FLAG_DISC_DISC:
                    return False
        self.game_finished = True
        return True

    def get_numb_flags(self, cords: tuple[int, int]) -> int:
        """ rend le nombre de drapeaux autour des coordonées données"""
        ret = 0
        for i in range(cords[1] - 1, cords[1] + 2):
            for j in range(cords[0] - 1, cords[0] + 2):
                if (j, i) == cords or j >= self._size[0] or j < 0 or i >= self._size[1] or i < 0:
                    continue
                if self.flag_discovered[i][j] == FLAG_DISC_FLAG:
                    ret += 1
        return ret

    def get_blanks(self, cords: tuple[int, int]) -> list[tuple[int, int]]:
        """ rend les coordonnées autour des coordonnées données qui sont non éxplorées et sans drapeau"""
        ret = []
        for i in range(cords[1] - 1, cords[1] + 2):
            for j in range(cords[0] - 1, cords[0] + 2):
                if (j, i) == cords or j >= self._size[0] or j < 0 or i >= self._size[1] or i < 0:
                    continue
                if self.flag_discovered[i][j] == FLAG_DISC_BLANK:
                    ret.append((j, i))
        return ret

    def get_numb_blanks(self, cords: tuple[int, int]) -> int:
        """ rend le nombre de cases non explorées et sans drapeaux autour des coordonnées données"""
        return len(self.get_blanks(cords))

    def discover_all_mines(self):
        """ rend visible toutes les mines et nous montre si nous nous étions trompés"""
        for i in range(self._size[1]):
            for j in range(self._size[0]):
                state = self.flag_discovered[i][j]
                if self.__is_mine((j, i)) and state == FLAG_DISC_BLANK:
                    # il y avait une mine et elle n'était pas marquée
                    self.flag_discovered[i][j] = FLAG_DISC_MINE
                elif not self.__is_mine((j, i)) and state == -1:
                    # mauvais drapeau (c'est à dire qu'il n'y avait pas de mine)
                    self.flag_discovered[i][j] = FLAG_DISC_WRONG_FLAG
                elif self.__is_mine((j, i)) and state == 1:
                    # on a cliqué sur une mine (raison de fin de partie)
                    self.flag_discovered[i][j] = FLAG_DISC_WRONG_CLICK

    def click(self, cords: tuple[int, int]) -> bool:
        """ retourne True si une mine a étée cliquée, False sinon"""
        if not self._game_started:
            self.__confirm_first_click(cords)
        cords_to_click = [cords]
        while cords_to_click:
            cur = cords_to_click.pop()
            if cur != cords and self.flag_discovered[cur[1]][cur[0]] == FLAG_DISC_DISC:
                continue
            self.flag_discovered[cur[1]][cur[0]] = FLAG_DISC_DISC

            # si cette condition est vraie alors ça ne peut que dire deux choses:
            # soit on c'est trompé sur la case cliquée soit un ou des drapeaux ont étés mal mis.
            if self.__is_mine(cur):
                self.discover_all_mines()
                self.lost = True
                self.game_finished = True
                return True

            # on vérifie si la case est apte à être cliquée c'est à dire s'il y a
            # autant de drapeaux autour de la case que de mines indiquées.
            if self.get_numb_flags(cur) == self.__get_numbs(cur):
                # on rajoute ici toutes les coordonnées qui n'ont pas été déjà cliquées ou qui
                # ne sont pas déjà dans la liste. (Pardon de la pythonnesquerie)
                cords_to_click += [
                    (i, j) for i in range(cur[0] - 1, cur[0] + 2) for j in range(cur[1] - 1, cur[1] + 2)
                    if (i, j) != cur and 0 <= i < self._size[0] and 0 <= j < self._size[1] and
                       (i, j) not in cords_to_click and self.flag_discovered[j][i] == FLAG_DISC_BLANK
                ]
        return False

    def put_flag(self, cords: tuple[int, int]) -> None:
        """ pose ou enlève un drapeau aux coordonées données."""
        if self.flag_discovered[cords[1]][cords[0]] == FLAG_DISC_FLAG:
            self.flag_discovered[cords[1]][cords[0]] = FLAG_DISC_BLANK
            self._numb_flags -= 1
        elif self.flag_discovered[cords[1]][cords[0]] == FLAG_DISC_BLANK:
            self.flag_discovered[cords[1]][cords[0]] = FLAG_DISC_FLAG
            self._numb_flags += 1

    def get_numb_mines(self) -> int:
        """ rend le nombre de mines supposées non découvertes"""
        return self._numb_mines - self._numb_flags

    def get_seen_board(self) -> list[list[int or str]]:
        """ rend la partie visible du démieur"""
        return [[
            self._mines[i][j] if (tmp := self.flag_discovered[i][j]) == FLAG_DISC_DISC else FLAG_DISC_CONV[tmp]
            for j in range(self._size[0])] for i in range(self._size[1])
        ]

    def __str__(self) -> str:
        if self._show_whole:
            ret = "WHOLE BOARD:\n"
            for i, row in enumerate(self._mines):
                for j, el in enumerate(row):
                    if self.__is_mine((j, i)):
                        ret += f"{MINE} "
                    else:
                        ret += f"{self._mines[i][j]} "
                ret += "\n"
        else:
            ret = ""
        ret += "SEEN BOARD:\n"
        for row in self.get_seen_board():
            for el in row:
                ret += f"{el} "
            ret += "\n"
        return ret[:-2]


class TestBoard(Board):
    """ juste pour tester des situations"""
    def __init__(self, mines, disc, size, numb_mines, starting_pos):
        super().__init__(size, numb_mines, show_whole=True)
        self._mines = mines
        self._starting_pos = starting_pos
        self.flag_discovered = disc
        self._game_started = True
