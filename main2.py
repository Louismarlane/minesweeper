""" Interface graphique"""
import time
import math

import pygame as pg
from locals import *
import main_board as mb
import ai


def choose():
    """ Fenêtre permettant de choisir le type de joueur (soi même ou l'ia)"""

    def buttons(texts: list[str], window_name: str):
        """ une fenêtre avec les boutons demandés"""
        pg.init()
        screen = pg.display.set_mode((BUTTON_HEIGHT * 2, BUTTON_HEIGHT * len(texts)))
        pg.display.set_caption(window_name)
        font = pg.font.Font("text/pixelart.ttf", BUTTON_TEXT_SIZE)

        button_img = pg.transform.scale(pg.image.load("images/bouton.png"), (BUTTON_HEIGHT * 2, BUTTON_HEIGHT))
        diff_texts = []
        for diff in texts:
            diff_texts.append(font.render(diff, True, BUTTON_TEXT_COLOR))
        finished = False
        while not finished:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()
                if event.type == pg.MOUSEBUTTONUP:
                    tmp = pg.mouse.get_pos()[1] // BUTTON_HEIGHT
                    pg.quit()
                    return tmp
            screen.fill((0, 0, 0))
            for i in range(len(texts)):
                screen.blit(button_img, (0, BUTTON_HEIGHT * i))
                screen.blit(diff_texts[i], (BUTTON_HEIGHT - (i_size := diff_texts[i].get_size())[0] / 2,
                                            BUTTON_HEIGHT / 2 - i_size[1] / 2 + BUTTON_HEIGHT * i))
            pg.display.flip()
        time.sleep(2)

    player = buttons(["Jouer", "IA"], "choisissez le joueur")
    difficulty = DIFFICULTES[str(buttons(["Debutant", "Medium", "Expert", "Surhomme", "Alien"],
                                         "choisissez la difficulté") + 1)]
    if player:
        continuous = False if buttons(["Continu", "Controle"], "") else True
        ia_game(*difficulty, continuous=continuous)
    else:
        player_game(*difficulty)


class Show:
    """ Nous permet d'afficher le jeu"""
    def __init__(self, board: mb.Board):

        size = board.get_size()
        self.size = size
        screen_w_over_h_ratio = SCREEN_SIZE[0] / (SCREEN_SIZE[1] - 100)
        cases_w_over_h_ratio = size[0] / size[1]

        # on modifie la taille des cases en fonction de la résolution de l'écran
        if SCREEN_SIZE[1] - 200 > size[1] * 32 and size[0] * 32 < SCREEN_SIZE[0] - 200:
            case_size = 32
        elif cases_w_over_h_ratio > screen_w_over_h_ratio:
            case_size = (SCREEN_SIZE[0] - 150) // size[0]
        else:
            case_size = (SCREEN_SIZE[1] - 150) // size[1]

        self.case_size = case_size

        # taille finale de la fenêtre
        self.screen_size = case_size * (size[0] + 1), case_size * (size[1] + 4)

        # on charge toutes les images à la bonne échelle
        self.numb_images = []
        for i in range(9):
            self.numb_images.append(pg.transform.scale(pg.image.load(f"images/{i}.png"), (case_size, case_size)))
        self.blank = pg.transform.scale(pg.image.load("images/blank.png"), (case_size, case_size))
        self.flag = pg.transform.scale(pg.image.load("images/flag.png"), (case_size, case_size))
        self.mine = pg.transform.scale(pg.image.load("images/mine.png"), (case_size, case_size))
        self.wrong = pg.transform.scale(pg.image.load("images/wrong.png"), (case_size, case_size))
        self.wrong_flag = pg.transform.scale(pg.image.load("images/wrong_flag.png"), (case_size, case_size))

        # tous les bords
        self.v_borders = pg.transform.scale(pg.image.load("images/border.png"),
                                            (case_size / 2, case_size * (size[1] + 3)))
        self.h_borders = pg.transform.scale(pg.transform.rotate(pg.image.load("images/border.png"), -90),
                                            (case_size * size[0], case_size / 2))
        self.nw_corner = pg.transform.scale(pg.image.load("images/nw_corner.png"), (case_size / 2, case_size / 2))
        self.ne_corner = pg.transform.scale(pg.image.load("images/ne_corner.png"), (case_size / 2, case_size / 2))
        self.sw_corner = pg.transform.scale(pg.image.load("images/sw_corner.png"), (case_size / 2, case_size / 2))
        self.se_corner = pg.transform.scale(pg.image.load("images/se_corner.png"), (case_size / 2, case_size / 2))

        self.w_intersection = pg.transform.scale(pg.image.load("images/w_intersection.png"),
                                                 (case_size / 2, case_size / 2))
        self.e_intersection = pg.transform.scale(pg.image.load("images/e_intersection.png"),
                                                 (case_size / 2, case_size / 2))

        # autre
        self.counter = []
        for i in range(10):
            self.counter.append(pg.transform.scale(pg.image.load(f"images/cd_{i}.png"),
                                                   (case_size, case_size * 114 / 64)))
        counter_height = case_size * 114 / 64
        self.counter_offset = (case_size + case_size * 2.5 - counter_height) / 2
        self.nb_mines = board.get_numb_mines()
        self.time = 0
        self.board = board
        # bouton pour recommencer
        self.smile = [pg.transform.scale(pg.image.load("images/smile.png"), (2 * case_size, 2 * case_size)),
                      pg.transform.scale(pg.image.load("images/sunglasses.png"), (2 * case_size, 2 * case_size)),
                      pg.transform.scale(pg.image.load("images/dead.png"), (2 * case_size, 2 * case_size))]
        self.cur_smile = 0

    def update(self) -> None:
        """ Juste vérifie si la partie est gagnée ou non (pour les emojis)"""
        if self.board.has_won():
            self.cur_smile = 1
        elif self.board.has_lost():
            self.cur_smile = 2
        else:
            self.cur_smile = 0

    def blit(self, screen: pg.Surface, around=None) -> None:
        """ Affiche le jeu à l'instant t"""

        # les bords verticaux
        screen.blit(self.v_borders, (0, self.case_size / 2))
        screen.blit(self.v_borders, (self.screen_size[0] - self.case_size / 2, self.case_size / 2))
        # les bords horizontaux
        screen.blit(self.h_borders, (self.case_size / 2, 0))
        screen.blit(self.h_borders, (self.case_size / 2, 3 * self.case_size))
        screen.blit(self.h_borders, (self.case_size / 2, self.screen_size[1] - self.case_size / 2))

        # les coins
        screen.blit(self.nw_corner, (0, 0))
        screen.blit(self.ne_corner, (self.screen_size[0] - self.case_size / 2, 0))
        screen.blit(self.sw_corner, (0, self.screen_size[1] - self.case_size / 2))
        screen.blit(self.se_corner, (self.screen_size[0] - self.case_size / 2,
                                     self.screen_size[1] - self.case_size / 2))
        screen.blit(self.w_intersection, (0, self.case_size * 3))
        screen.blit(self.e_intersection, (self.screen_size[0] - self.case_size / 2, self.case_size * 3))

        # le temps et le nombre de mines restantes
        if self.board.has_game_started() and not self.board.game_finished:
            self.time = time.time() - self.board.starting_time
            if self.time >= 999:
                self.time = 999
        cur_time = math.floor(self.time)
        for i in range(3):
            screen.blit(self.counter[cur_time // (100 // (10 ** i))],
                        (self.screen_size[0] - (self.counter_offset + self.case_size * (3 - i)),
                         self.counter_offset))
            cur_time %= 100 // (10 ** i)
        self.nb_mines = self.board.get_numb_mines()
        nb_mines = self.nb_mines if self.nb_mines < 1000 else 999
        for i in range(3):
            screen.blit(self.counter[nb_mines // (100 // (10 ** i))],
                        (self.counter_offset + i * self.case_size,
                         self.counter_offset))
            nb_mines %= 100 // (10 ** i)

        # le bouton "smile"
        screen.blit(self.smile[self.cur_smile],
                    (self.screen_size[0] / 2 - self.case_size, self.case_size * 3 / 4))

        # le jeu en soi
        seen = self.board.get_seen_board()
        for i, row in enumerate(seen):
            for j, el in enumerate(row):
                cur_cor = (0.5 + j) * self.case_size, (3.5 + i) * self.case_size
                if "0" <= str(el) <= "8":
                    screen.blit(self.numb_images[el], cur_cor)
                elif el == BLANK_CASE:
                    screen.blit(self.blank, cur_cor)
                elif el == FLAG:
                    screen.blit(self.flag, cur_cor)
                elif el == MINE:
                    screen.blit(self.mine, cur_cor)
                elif el == WRONG_FLAG:
                    screen.blit(self.wrong_flag, cur_cor)
                elif el == WRONG_CLICK:
                    screen.blit(self.wrong, cur_cor)
        if around is None:
            return
        if self.board.flag_discovered[around[1]][around[0]] == FLAG_DISC_FLAG:
            return
        for el in (self.board.get_blanks(around) if self.board.flag_discovered[around[1]][around[0]] > 0 else [around]):
            screen.blit(self.numb_images[0], (self.case_size * (0.5 + el[0]), self.case_size * (3.5 + el[1])))


def ia_game(size: tuple[int, int], nb_mines: int, continuous: bool = True):
    """ Fera jouer l'ia sans fin jusqu'à ce que la fenêtre soit fermée"""
    pg.init()
    board = mb.Board(size, nb_mines)

    # cela nous permet d'afficher tous les objets (jeu inclus)
    all_shown = Show(board)
    screen = pg.display.set_mode(all_shown.screen_size)
    ia = ai.Ai(board)
    cmd = ia.lvl2()

    # puis finalement on peut faire tourner l'ia
    while True:
        finished = False
        while not finished:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    quit()

            next(cmd)
            screen.fill((170, 170, 170))
            all_shown.update()
            all_shown.blit(screen)
            if board.has_won() or board.has_lost():
                finished = True
            pg.display.flip()
        if not continuous:
            finished = False
        else:
            time.sleep(0.5)
        while not finished:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    quit()
                # si il clique sur le bouton "smile"
                if event.type == pg.MOUSEBUTTONUP:
                    if -all_shown.case_size <= (pos := pg.mouse.get_pos())[0] - (all_shown.screen_size[0] / 2) <= \
                            all_shown.case_size and 0 <= pos[1] - all_shown.case_size * 3 / 4 <= \
                            2 * all_shown.case_size:
                        finished = True
            screen.fill((170, 170, 170))
            all_shown.blit(screen)
        board = mb.Board(size, nb_mines)
        all_shown = Show(board)
        ia = ai.Ai(board)
        cmd = ia.lvl2()


def player_game(size: tuple[int, int], nb_mines):
    """ fait une infinité de parties avec le joueur"""
    pg.init()
    board = mb.Board(size, nb_mines)

    def is_mouse_on_board() -> bool:
        """ rend si la souris est sur l'une des cases"""
        m_pos = pg.mouse.get_pos()
        return all_shown.case_size / 2 < m_pos[0] <= all_shown.screen_size[0] - all_shown.case_size / 2 and \
               all_shown.case_size * 3.5 < m_pos[1] <= all_shown.screen_size[1] - all_shown.case_size / 2

    def get_mouse_cords_on_board() -> tuple[int, int]:
        """ rend la case sur laquelle la souris est"""
        m_pos = pg.mouse.get_pos()
        pos_on_board = round(m_pos[0] - all_shown.case_size / 2), round(m_pos[1] - all_shown.case_size * 3.5)
        return pos_on_board[0] // all_shown.case_size, pos_on_board[1] // all_shown.case_size
    # cela nous permet d'afficher tous les objets (jeu inclus)
    all_shown = Show(board)
    screen = pg.display.set_mode(all_shown.screen_size)
    # puis finalement on peut faire tourner l'ia
    pressed = pg.mouse.get_pressed()
    finished = False
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()
            if event.type == pg.MOUSEBUTTONUP:
                if -all_shown.case_size <= (pos := pg.mouse.get_pos())[0] - (all_shown.screen_size[0] / 2) <= \
                        all_shown.case_size and 0 <= pos[1] - all_shown.case_size * 3 / 4 <= \
                        2 * all_shown.case_size:
                    finished = False
                    board = mb.Board(size, nb_mines)
                    all_shown = Show(board)
                elif is_mouse_on_board() and not finished:
                    cur_pressed = pg.mouse.get_pressed()
                    cords_on_board = get_mouse_cords_on_board()
                    if pressed[0] and not cur_pressed[0]:
                        board.click(cords_on_board)
                    elif pressed[2] and not cur_pressed[2]:
                        board.put_flag(cords_on_board)
        pressed = pg.mouse.get_pressed()
        around = None
        if pressed[0] and is_mouse_on_board() and not finished:
            around = get_mouse_cords_on_board()
        screen.fill((170, 170, 170))
        all_shown.update()
        all_shown.blit(screen, around)
        if board.has_won() or board.has_lost():
            finished = True
        pg.display.flip()


if __name__ == "__main__":
    choose()
