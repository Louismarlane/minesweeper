""" AI servant a résoudre le jeu démineur"""

import main_board
import random
from locals import *


class Box:
    """ Contiendra entre 1 et 8 cases et le nombre de mines dedans ou le nombre maximal de mines (selon la situation)"""

    def __init__(self, box_cords: list[tuple[int, int]], numb_mines: int):
        self.box_cords = box_cords
        self.numb_mines = numb_mines
        self.min_included: list["Box"] = []
        self.max_included: list["Box"] = []

    def get_intesection(self, other: "Box") -> list[tuple[int, int]]:
        """ rend les coordonnées contenant l'intersection de deux boites (les cases en commun)"""
        ret = []
        for el in self.box_cords:
            if el in other.box_cords:
                ret.append(el)
        return ret

    def is_other_included_in(self, other: "Box") -> bool:
        """ rend True si la boite donnée est incluse dans celle là, False sinon"""
        for el in other.box_cords:
            if el not in self.box_cords:
                return False
        return True

    def get_dist(self, other: "Box") -> int:
        """ rend la distance carrée entre deux cases au hazard dans les boites"""
        return sum([(self.box_cords[0][i] - other.box_cords[0][i]) ** 2 for i in range(2)])

    def can_collide(self, other: "Box") -> bool:
        """ rend si deux boites ont une possibilité d'avoir une ou des cases en commun"""
        return self.get_dist(other) <= 32  # distance minimale pour que deux boites aient une possibilité de se toucher

    def remove(self, tab: list[tuple[int, int]]) -> list[tuple[int, int]]:
        """ rend sa liste de coordonnées sans les éléments donnés en paramètres"""
        return [el for el in self.box_cords if el not in tab]

    def is_equal(self, other: "Box") -> bool:
        """ rend si les deux boites ont les mêmes cases c'est à dire A est incluse dans B et B incluse dans A"""
        return other.is_other_included_in(self) and self.is_other_included_in(other) \
               and self.numb_mines == other.numb_mines

    def do_intersect(self, other: "Box") -> bool:
        """ rend True si les deux boites ont des cases en commun"""
        return len(self.get_intesection(other)) > 0

    def make_intersection(self, _min: "Box", _max: "Box") -> tuple[str, list[tuple[int, int]]] \
                                                       or tuple[str, list["Box"]] or None:
        """ rend une action si possible avec l'intersection de une boite "minimum" et une boite "maximum" """
        if not (s := _min.is_equal(_max)) and _min.do_intersect(_max):
            if len(tmp := _min.remove(_max.box_cords)) == (q := _min.numb_mines - _max.numb_mines) and q:
                return FLAG_COMAND, tmp
            elif len(tmp) > q > 0:
                self.min_included.append(Box(tmp, q))
                return None
        elif s and _min.numb_mines == _max.numb_mines:
            if len(r := _min.box_cords) == _min.numb_mines:
                return FLAG_COMAND, r
            if _min.numb_mines == 0:
                return CLICK_COMAND, r
            return NEW_BOX_COMAND, [Box(_min.box_cords[:], _min.numb_mines)]

    def _is_box_in_min(self, box: "Box"):
        """ rend si la boite de type "min" est dans la liste des min"""
        for el in self.min_included:
            if el.is_equal(box):
                return True
        return False

    def _is_box_in_max(self, box: "Box"):
        """ rend si la boite de type "max" est dans la liste des max"""
        for el in self.max_included:
            if el.is_equal(box):
                return True
        return False

    def __str__(self):
        return str(self.box_cords) + f"\nn_mines = {self.numb_mines}"

    def determine(self, other: "Box") -> tuple[str, list[tuple[int, int]]] or tuple[str, list["Box"]] or None:
        """ rend une action et les coordonnées sur lesquelles performer cette action"""
        if self.numb_mines == 0:
            return CLICK_COMAND, self.box_cords
        if len(self.box_cords) == self.numb_mines:
            return FLAG_COMAND, self.box_cords

        # cas dans lequel une boite est incluse dans l'autre.
        if (s := self.is_other_included_in(other)) or other.is_other_included_in(self):
            tmp = self.remove(other.box_cords) if s else other.remove(self.box_cords)
            if not tmp:
                return None
            if len(tmp) == (q := abs(other.numb_mines - self.numb_mines)):
                # si on est sur que toutes les autres cases sont des mines
                return FLAG_COMAND, tmp
            if q == 0:
                # si on est sur que toutes les autres cases ne sont pas des mines
                return CLICK_COMAND, tmp
            if len(tmp) == q:
                return FLAG_COMAND, tmp
            else:
                # sinon on crée juste une autre boite avec le nombre de mines restantes (la boite self sera supprimée)
                return NEW_BOX_DEL_COMAND, [Box(tmp, q)]
        if len(tmp := self.get_intesection(other)) > 0:
            if other.numb_mines < self.numb_mines:
                # trop dur à expliquer en texte, il me faudrait un schéma
                new_max = Box(tmp, other.numb_mines)
                new_min = Box(self.remove(tmp), self.numb_mines - other.numb_mines)
                if len(resp := new_min.box_cords) == new_min.numb_mines > 0:
                    return FLAG_COMAND, resp
                for el in self.min_included:
                    if (com := self.make_intersection(el, new_max)) is not None:
                        return com
                for el in self.max_included:
                    if (com := self.make_intersection(new_min, el)) is not None:
                        return com
                if not (is_max := self._is_box_in_max(new_max)):
                    self.max_included.append(new_max)
                if not (is_min := self._is_box_in_min(new_min)):
                    self.min_included.append(new_min)
                if is_max and is_min:
                    return None
                for o_min in other.min_included:
                    for s_max in self.max_included:
                        if (com := self.make_intersection(o_min, s_max)) is not None:
                            return com
                for o_max in other.max_included:
                    for s_min in self.min_included:
                        if (com := self.make_intersection(s_min, o_max)) is not None:
                            return com
                return DID_SOMETHING, []
        return None


class Ai:
    """ Ai qui tente de résoudre une partie de démieur"""

    def __init__(self, board: main_board.Board):
        self.board = board
        self.numb_mines = self.board.get_numb_mines()
        self.size = self.board.get_size()

    def go_throught(self) -> str:
        """ si une case a le même nombre de cases vides (drapeaux inclus) et son nombre,
        cette fonction posera des drapeaux sur toutes les cases vides
        de la même manière, si une case a le même nombre de drapeaux autour que son nombre,
        cette fonction "cliquera" une seule fois dessus.

        elle rend les cases qu'elle a alteré en donnant la fonction utilisée (noms visibles dans locals.py)
        tout dans une chaine de caractère dans le but d'être lisible par un programme après
        et possiblement faire évoluer cette IA en aide en jouant.
        """
        seen_board = self.board.get_seen_board()
        for i in range(self.size[1]):
            for j in range(self.size[0]):
                # on vérifie que la case qu'on observe est bien visible et "cliquable" et non nule
                if (numb := seen_board[i][j]) != BLANK_CASE and numb != FLAG and numb:
                    cur = (j, i)
                    nb_b = self.board.get_numb_blanks(cur)
                    nb_f = self.board.get_numb_flags(cur)

                    # si il y a autant de drapeaux que le nombre de la case et il y a des cases vides
                    if nb_f == numb and nb_b:
                        self.board.click((j, i))
                        return f"{CLICK_COMAND},{j} {i}"

                    # si il y a autant de cases vides que de mines autour restantes
                    elif nb_b + nb_f == numb and nb_b:
                        ret = f"{FLAG_COMAND},"
                        for el in self.board.get_blanks(cur):
                            self.board.put_flag(el)
                            ret += f"{el[0]} {el[1]},"
                        return ret[:-1]
        return ""

    def click_most_likely(self) -> str:
        """ clique sur une case au hazard
        celle qui a une chance minimale d'être une mine
        """
        seen_board = self.board.get_seen_board()

        min_pos = []
        action = ""
        chance = 0  # chances de ne pas perdre en faisant l'action donnée
        blanks = []
        for i in range(self.size[1]):
            for j in range(self.size[0]):
                if (numb := seen_board[i][j]) != BLANK_CASE and numb != FLAG and numb and numb - (
                        nb_f := self.board.get_numb_flags((j, i))) > 0:

                    # on calcule la chance d'avoir bon en cliquant au hazard autour de la case
                    if (cur_ch := (1 - (numb - nb_f) / len(bks := self.board.get_blanks((j, i))))) > chance:
                        chance = cur_ch
                        action = CLICK_COMAND
                        min_pos = bks
                elif numb == BLANK_CASE:
                    blanks.append((j, i))

        if not min_pos:
            self.board.click(tmp := random.choice(blanks))
            return f"{CLICK_COMAND},{tmp[0]} {tmp[1]}"

        final = random.choice(min_pos)
        if action == CLICK_COMAND:
            self.board.click(final)
        elif action == FLAG_COMAND:
            self.board.put_flag(final)
        return f"{action},{final[0]} {final[1]}"

    def boxed_analisis(self) -> str:
        """ Cette fonction rend une ou des cases dont on est sur qu'on peut cliquer ou mettre un drapeau
        en utilisant des groupes de boites
        """
        seen = self.board.get_seen_board()
        boxes = []

        # on ajoute en premier toutes les "boites" disponibles.
        for i in range(self.size[1]):
            for j in range(self.size[0]):
                if not type(seen[i][j]) == int:
                    continue
                if (numb := seen[i][j] - self.board.get_numb_flags((j, i))) > 0 \
                        and len(tmp := self.board.get_blanks((j, i))) > 0:
                    boxes.append(Box(tmp, numb))
        done_something = True
        while done_something:
            done_something = False
            for i, el in enumerate(boxes[:]):
                for el2 in boxes[:]:
                    if el == el2 or not el.can_collide(el2):
                        continue
                    if (cur_com := el.determine(el2)) is None:
                        continue
                    if cur_com[0] == NEW_BOX_COMAND:
                        for box in cur_com[1]:
                            for a_box in boxes:
                                if a_box.is_equal(box):
                                    break
                            else: continue
                            boxes.append(box)
                            done_something = True
                    elif cur_com[0] == NEW_BOX_DEL_COMAND:
                        boxes.pop(i)
                        boxes.append(cur_com[1][0])
                        done_something = True
                        break
                    elif cur_com[0] == DID_SOMETHING:
                        done_something = True
                    else:
                        if cur_com[0] == FLAG_COMAND:
                            for j in cur_com[1]:
                                self.board.put_flag(j)
                        if cur_com[0] == CLICK_COMAND:
                            for j in cur_com[1]:
                                self.board.click(j)
                        return f"{cur_com[0]}," + ",".join([f"{i[0]} {i[1]}" for i in cur_com[1]])
                else: continue
                break
        return ""

    def lvl1(self) -> str:
        """ tant que la fonction go_throught ne rend pas rien, cette foncion va l'executer.
        ensuite elle choisit une case au hazard.

        ça serait le premier niveau d'ia au démieur qui ne va pas
        plus loin que ce qu'on voit au premier coup d'oeuil.
        """
        finished = False
        while not finished:
            if tmp := self.go_throught():
                yield tmp
            else:
                yield self.click_most_likely()
            if self.board.has_won() or self.board.has_lost():
                finished = True

    def lvl2(self):
        """ le niveau 2 se divise en 3 étapes:
        - en premier il s'occupe de tout ce qui est "niveau 1"
        - puis fait une analyse "en boites" pour avoir une action sure
        - sinon on fait recours au hazard.

        Après chaque action, on recommence tout (je ne me suis pas concentré sur l'efficacité du programme)

        rend à chaque fois l'action et les coordonnées des cases dont l'action a été performée.
        """
        finished = False
        while not finished:
            if not self.board.has_game_started():
                self.board.click(st := (self.board.get_size()[0] // 2, self.board.get_size()[1] // 2))
                yield f"{CLICK_COMAND},{st[0]} {st[1]}"
            if tmp := self.go_throught():
                yield tmp
            elif tmp := self.boxed_analisis():
                yield tmp
            else:
                yield self.click_most_likely()

            if self.board.has_won() or self.board.has_lost():
                finished = True
