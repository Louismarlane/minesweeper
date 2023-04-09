""" fichier faisant tourner le jeu de démieur"""

import main_board as mb
from locals import *
import ai


def get_input(control: mb.Board, inp: str):
    """ Permet de convertir un input en commande"""
    com = inp[0]
    numbs = [int(t) for t in inp[2:].split(" ")]
    cords: tuple[int, int] = numbs[0], numbs[1]
    if inp.startswith(FLAG_COMAND):
        control.put_flag(cords)
        print(board)
        print(f"mines restantes: {board.get_numb_mines()}")

    elif com == CLICK_COMAND:
        control.click(cords)
        print(board)
        print(f"mines restantes: {board.get_numb_mines()}")


def convert_into_board(mines_g: list[str], sp: tuple[int, int]) -> mb.TestBoard:
    """ me sert pour tester,
    copie une partie de démieur sans grand efforts
    """
    mines = []
    nb_mines = 0
    for el in mines_g:
        mines.append(tmp := [])
        for numb in el.split(" "):
            if numb == MINE:
                nb_mines += 1
                tmp.append(-1)
            else:
                tmp.append(int(numb))
    taille = len(mines[0]), len(mines)
    disc = [[0 for _ in range(taille[0])] for _ in range(taille[1])]
    ret_board = mb.TestBoard(mines, disc, taille, nb_mines, sp)
    ret_board.click(sp)
    return ret_board


testint = ["2 2 2 2 2 2 Ω Ω Ω 2",
           "Ω Ω 4 Ω Ω 4 3 4 4 Ω",
           "3 Ω Ω 4 Ω Ω 2 2 Ω 2",
           "1 3 3 3 2 3 Ω 2 2 2",
           "0 2 Ω 3 1 1 1 1 1 Ω",
           "0 2 Ω Ω 1 0 1 1 2 1",
           "1 2 4 3 2 0 1 Ω 1 0",
           "3 Ω 3 Ω 1 0 1 1 2 1",
           "Ω Ω 5 3 3 1 2 2 3 Ω",
           "Ω 4 Ω Ω 2 Ω 2 Ω Ω 2"]

test2 = ["Ω 1 1 1",
         "2 2 2 Ω",
         "1 Ω 2 1",
         "1 1 1 0"]

if __name__ == "__main__":
    while True:
        difficulte = input("Choisissez la difficulté (1-5):\n"
                           "Débutant: 9x9 avec 10 mines\n"
                           "Intermédiaire: 16x16 avec 40 mines\n"
                           "Avancé: 30x16 avec 99 mines\n"
                           "Surhomme: 50x50 avec 500 mines\n"
                           "Extraterrestre: 100x100 avec 2000 mines\n"
                           "Votre choix: ")
        board = mb.Board(*DIFFICULTES[difficulte])
        choix_du_joueur = input("Regarder l'IA jouer: 1\n"
                                "Lancer une partie de démieur: 2\n"
                                "Votre choix: ")
        if choix_du_joueur == "1":
            par_etapes = input("Vitesse contrôlée?(oui/non): ")
            input("pour chaque étape, \n"
                  "f c'est pour mettre un ou des drapeaux aux coordonées données\n"
                  "c c'est cliquer aux coordonnées données")
            board.click(co_debut := ((size := board.get_size())[0] // 2, size[1] // 2))
            print(f"c,{co_debut[0]} {co_debut[1]}")
            print(board)
            print(f"il reste {board.get_numb_mines()}")
            ia = ai.Ai(board)
            commandes = ia.lvl2()
            if par_etapes == "oui":
                for commande in commandes:
                    input("enter pour passer à l'étape suivante")
                    print(commande, board, f"il reste {board.get_numb_mines()} mines\n", sep="\n")
            elif par_etapes == "non":
                for commande in commandes:
                    print(commande, board, f"il reste {board.get_numb_mines()} mines\n", sep="\n")
            if board.has_won():
                print("L'IA a gagné!")
            elif board.has_lost():
                print("L'IA a perdu...")
        elif choix_du_joueur == "2":
            print("Pour jouer, il faut mettre en premier l'action (c ou f pour cliquer ou poser un drapeau)\n"
                  "puis les coordonées. Tout doit être séparé par un espce : exemple : c 5 5")
            print(board)
            while not board.has_lost() and not board.has_won():
                commande_j = input("Votre action: ")
                if commande_j:
                    get_input(board, commande_j)
            if board.has_won():
                print("Vous avez gagné!")
            if board.has_lost():
                print("Vous avez perdu...")
        if input("Voulez-vous quitter ?(oui/non)") == "oui":
            quit()
    # cmd = ia.lvl1()
    # for i in range(20000):
    #     for _ in cmd:
    #         pass
    #     if board.has_won():
    #         nb_p += 1
    #     board = mb.Board((30, 16), 99, (10, 10))
    #     print(f"{round((i / 20000) * 100, 1)}%")
    #     ia = ai.Ai(board)
    #     cmd = ia.lvl2()
    # print(f"winrate : {nb_p / 20000 * 100}%")
