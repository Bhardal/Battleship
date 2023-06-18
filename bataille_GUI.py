from cgitb import reset
import tkinter as tk
import random as rd
from PIL import Image, ImageTk
import tkinter.messagebox as tk_msg_box
from bataille_navale import *
import sys
# import time as t

square_size = 30
board_size = square_size*10

instructions = """
Appuyer sur 'Démarrer' pour lancer une partie
Il est possible à tout moment d'arrêter la partie en cours avec le bouton 'Arrêter'
Le jeu se déroule en plusieurs phases :
    - Vous placer vos bateaux sur la grille
    - Une fois prêt, vous lancer la partie en appuyant sur 'Démarrer'
    - Vous commencer en attaquant, pour cela vous appuyer sur une des cases de la grille de l'IA
    - Les symboles indiquent si le coup est 'A l'eau', 'Touché' ou 'Touché-Coulé'
    - L'IA joue à son tour, vous verrez s'afficher sur votre grille son action de la même manière
    - Le premier a avoir perdu l'entièreté de ses bateaux perd !

Bon jeu !
"""


class Grid:
    def __init__(self, canv, size, placeable_ships={}):
        self.canv = canv
        self.size = size
        self.reset()
        # If it has placeable ships, it adds special functionalities
        if placeable_ships:
            self.canv.bind("<1>", self.select_ship)
            # Create menu :
            self.add_ship_menu()

    def reset(self):
        self.board = [[0 for _ in range(self.size)] for _2 in range(self.size)]
        self.attacker_ships = []

    """ === Ship placement === """

    def select_ship(self, event):
        near = self.canv.find_closest(event.x, event.y)

        if "ship" in self.canv.gettags(near):
            self.canv.bind("<Motion>", self.move_ship)
            self.canv.bind('<ButtonRelease-1>', self.deselect_ship)
            self.canv.bind('<Button-3>', self.rotate)

            self.canv.addtag_withtag('selected', tk.CURRENT)

    def deselect_ship(self, event):
        self.canv.dtag('selected')
        self.canv.unbind('<Motion>')
        self.canv.unbind('<Button-3>')

    def move_ship(self, event):
        x, y = event.x, event.y
        square_x, square_y = x//square_size, y//square_size

        tags = self.canv.gettags("selected")
        if "ship2" in tags:
            i = 0
        elif "ship3" in tags:
            i = 1
        elif "ship3_1" in tags:
            i = 2
        elif "ship4" in tags:
            i = 3
        elif "ship5" in tags:
            i = 4

        ships = [list(self.attacker_ships[j].coords) for j in range(5)]
        ships.pop(i)
        self.attacker_ships[i].place([square_x, square_y], ships)

        self.canv.delete("selected")
        self.update(self.attacker_ships[i])

    def rotate(self, event):
        # el = self.canv.find_withtag('selected')[0]
        tags = self.canv.gettags("selected")

        if "ship2" in tags:
            i = 0
        elif "ship3" in tags:
            i = 1
        elif "ship3_1" in tags:
            i = 2
        elif "ship4" in tags:
            i = 3
        elif "ship5" in tags:
            i = 4

        ships = [list(self.attacker_ships[j].coords) for j in range(5)]
        ships.pop(i)
        self.attacker_ships[i].rotate(ships)
        self.canv.delete("selected")
        self.update(self.attacker_ships[i])

    """ === Ship Menu/Info === """

    def add_ship_menu(self):
        """
        Adds the menu at the bottom to add ships, and places them too
        """
        self.canv.configure(height=board_size+5*square_size)
        self.canv.create_rectangle(
            0, board_size, board_size, board_size+5*square_size, fill='lightgrey')

        ship_infos = ((2, 1, [0, 10], 2, "./images/ship5"),
                      (3, 1, [2, 10], 3, "./images/ship3"),
                      (3, 1, [4, 10], "3_1", "./images/ship3"),
                      (4, 1, [6, 10], 4, "./images/ship2"),
                      (5, 1, [8, 10], 5, "./images/ship1"))

        self.canv.images = []
        self.canv.images_hor = []
        for infos in ship_infos:
            length, orientation, coords, tag, file = infos

            image, image_hor = Image.open(
                f"{file}.png"), Image.open(f"{file}_hor.png")
            self.attacker_ships.append(Battleship(
                length, orientation, coords, img=image, img_hor=image_hor, tag=tag))

            self.canv.images.append(
                ImageTk.PhotoImage(self.attacker_ships[-1].img.resize((square_size, square_size*length), Image.ANTIALIAS)))
            self.canv.images_hor.append(ImageTk.PhotoImage(
                self.attacker_ships[-1].img_hor.resize((square_size*length, square_size), Image.ANTIALIAS)))

            # print(self.img)
            # img = tk.PhotoImage(file=file)
            self.canv.create_image(
                coords[0]*square_size+square_size//2, coords[1]*square_size+length*square_size//2, image=self.canv.images[-1], tags=f"ship{tag}")

            self.canv.addtag_withtag("ship", f"ship{tag}")
        print(self.canv.images)
        print(self.canv.images_hor)

    def is_dead(self):
        """
        If all AI ships are dead, returns True
        """
        for ship in self.attacker_ships:
            if not ship.is_dead:
                break
        else:
            return True

    """ === Attack === """

    def attack(self, coords):
        """
        If the cell already has an action (something else than 0) then don't do anything
        Otherwise : attack the cell
        """
        x, y = coords
        if self.board[y][x] == 0:
            for ship in self.attacker_ships:
                # print(list(ship.coords.keys()), (x, y))
                # checks if coords is one of a boat

                if (x, y) in list(ship.coords.keys()):
                    self.board[y][x] = 2
                    ship.hit()
                    # checks if all other ship parts have been hit
                    for coord in ship.coords:
                        x2, y2 = coord
                        if not self.board[y2][x2]:
                            break
                    # if all other ship parts have been hit
                    else:
                        ship.is_dead = 1
                        for coord in ship.coords:
                            x2, y2 = coord
                            self.board[y2][x2] = 3
                    break
                # coord is not part of a boat
                else:
                    self.board[y][x] = 1
            # for line in self.board:
            #     print(line)
            self.update_board()
        else:
            # user clicked on a cell that was already selected
            pass

        if self.is_dead():
            pop_up("La partie est finie :", "Vous avez perdu !")
            return False
        turn_label["text"] = "Au tour du joueur !"
        return True

    # Traces the lines in the background
    def trace(self, size):
        self.canv.delete('background')
        for i in range(size):
            self.canv.create_line(
                0, i*square_size, 10*square_size, i*square_size, tag='background', fill='black')
            self.canv.create_line(
                i*square_size, 0, i*square_size, 10*square_size, tag='background', fill='black')

    def update(self, boat):
        """
        Redraws the boat given as a parameter
        """
        tag_to_index = {
            "2": 0,
            "3": 1,
            "3_1": 2,
            "4": 3,
            "5": 4
        }
        x, y = list(boat.coords)[0]
        size = boat.length
        dire = boat.ori
        if not dire:  # horizontal

            index = tag_to_index[str(boat.tag)]
            self.canv.create_image(
                x*square_size+size*square_size//2, y*square_size+square_size//2,
                image=self.canv.images_hor[index], tags=f"ship{boat.tag}")

        else:  # vertical

            self.canv.create_image(
                x*square_size+square_size//2, y*square_size+size*square_size//2,
                image=self.canv.images[tag_to_index[str(boat.tag)]], tags=f"ship{boat.tag}")

        self.canv.addtag_withtag("ship", f"ship{boat.tag}")
        self.canv.addtag_withtag("selected", f"ship{boat.tag}")

    def update_board(self):
        """
        Updates the board, with the correct logos corresponding to different events :
        - 1 : Miss
        - 2 : Hit
        - 3 : Hit-Sunk
        """
        self.canv.delete("logo")
        for line_i, line in enumerate(self.board):
            for column_i, el in enumerate(line):
                if el:
                    self.canv.create_image(
                        column_i*square_size+square_size//2, line_i*square_size+square_size//2, image=symbol_imgs[int(el)-1], tags="logo")

    """ === Controls === """


class AI_Grid(Grid):
    def __init__(self, canv, size):
        self.canv = canv
        self.size = size
        self.reset()

    def reset(self):
        self.board = [[0 for _ in range(self.size)] for _2 in range(self.size)]
        self.ai_tries = [[0 for _ in range(self.size)]
                         for _2 in range(self.size)]
        self.ai_ships = []
        self.canv.unbind("<1>")

    def attack(self, event):
        """
        If the cell already has an action (something else than 0) then don't do anything
        Otherwise : attack the cell
        """
        self.canv.unbind("<1>")
        x, y = event.x//square_size, event.y//square_size
        # print(f"Attacking {x}, {y}... {self.board[y][x]}")

        if self.board[y][x] == 0:
            for ship in self.ai_ships:
                # print(list(ship.coords.keys()), (x, y))
                # checks if coords is one of a boat

                if (x, y) in list(ship.coords.keys()):
                    self.board[y][x] = 2
                    ship.hit()
                    # checks if all other ship parts have been hit
                    for coord in ship.coords:
                        x2, y2 = coord
                        if not self.board[y2][x2]:
                            break
                    # if all other ship parts have been hit
                    else:
                        ship.is_dead = 1
                        for coord in ship.coords:
                            x2, y2 = coord
                            self.board[y2][x2] = 3
                    break
                # coord is not part of a boat
                else:
                    self.board[y][x] = 1
            # for line in self.board:
            #     print(line)
            self.update()
            self.ai_attack()
        else:
            # user clicked on a cell that was already selected
            pass

        if self.is_dead():
            pop_up("La partie est finie :", "Vous avez gagné !")
            self.canv.unbind("<1>")  # to prevent playing from attacking again
        turn_label["text"] = "Au tour du joueur !"

    def ai_attack(self):
        """
        Picks randomly a spot it hasn't yet tried
        """
        # print("AI is attacking")
        is_valid = False
        # print(self.ai_tries)
        while not is_valid:
            x, y = rd.randint(0, 9), rd.randint(0, 9)

            # print(y, x)
            if self.ai_tries[y][x] == 0:
                self.ai_tries[y][x] = 1
                is_valid = True
                # print("Valid attack : ", (x, y))
                if not attacker_grid.attack((x, y)):
                    self.canv.unbind("<1>")
                    return True
        self.canv.bind("<1>", self.attack)

    def update(self):
        """
        Updates the board, with the correct logos corresponding to different events :
        - 1 : Miss
        - 2 : Hit
        - 3 : Hit-Sunk
        """
        self.canv.delete("logo")
        for line_i, line in enumerate(self.board):
            for column_i, el in enumerate(line):
                if el:
                    self.canv.create_image(
                        column_i*square_size+square_size//2, line_i*square_size+square_size//2, image=symbol_imgs[int(el)-1], tags="logo")

    def start(self):
        """
        Places its ships, adds the left click button
        """
        # print("Generating boats...")
        self.generate_rd_boats()
        self.canv.bind("<1>", self.attack)
        turn_label["text"] = "Au tour du joueur !"

    def generate_rd_boats(self):
        """
        It generates a random placement of ships, and fills the ai_ships list with all the ship objects
        """
        ai_board = [[0 for _ in range(self.size)] for _2 in range(self.size)]

        ship_sizes = (5, 4, 3, 3, 2)

        for size in ship_sizes:
            is_placed = False
            # place ship
            while not is_placed:
                x, y, direc = rd.randint(0, self.size), rd.randint(
                    0, self.size), rd.randint(0, 1)

                # vertical
                if direc:
                    try:
                        if not sum(ai_board[y][x:x+size]):
                            for i in range(x, x+size):
                                ai_board[y][i] = 1
                            is_placed = True
                            self.ai_ships.append(Battleship(size, 0, (x, y)))
                    except IndexError:
                        pass
                # horizontal
                else:
                    try:
                        if not sum(ai_board[y:y+size][x]):
                            for i in range(y, y+size):
                                ai_board[i][x] = 1
                            is_placed = True
                            self.ai_ships.append(Battleship(size, 1, (x, y)))
                    except IndexError:
                        pass
        # for line in ai_board:
        #     print(line)

    def is_dead(self):
        """
        If all AI ships are dead, returns True
        """
        for ship in self.ai_ships:
            if not ship.is_dead:
                break
        else:
            return True


def verify_boats():
    """
    Checks if all boats are actually on the grid, if not, returns False
    """
    for ship in attacker_grid.attacker_ships:
        if not (0 <= ship.m_coord[0] <= 9 and 0 <= ship.m_coord[1] <= 9):
            return False
    return True


def start_stop():
    """
    Stars the game, changes the text of the button accordingly
    """
    global running
    if not running:
        if not verify_boats():
            pop_up('Erreur', 'Tous tes bateaux ne sont pas sur la grille !')
            return False
        running = 1
        start_btn["text"] = "Arrêter"
        ai_grid.start()
    else:
        fen.destroy()
        sys.exit()


def pop_up(title, message):
    """
    Opens an information dialog
    """
    msg_box = tk_msg_box.showinfo(title, message)


fen = tk.Tk()
fen.geometry('700x600')
fen.title("Bataille Navale")
fen.resizable(0, 0)

img_path = ["miss", "hit", "dead"]
symbol_imgs = [ImageTk.PhotoImage(Image.open(f"./images/{filename}.png").resize(
    (square_size, square_size))) for filename in ["miss", "hit", "dead"]]


attacker_canv = tk.Canvas(fen, width=board_size,
                          height=board_size, bg="white")
attacker_canv.place(x=20, y=50)
ai_grid_label = tk.Label(fen, text="Votre grille", width=10)
ai_grid_label.place(x=20 + board_size//2 - 20, y=20)


ai_canv = tk.Canvas(fen, width=board_size,
                    height=board_size, bg="white")
ai_canv.place(x=30+10*square_size, y=50)
ai_grid_label = tk.Label(fen, text="Grille de l'IA", width=10)
ai_grid_label.place(x=(30+board_size) + board_size//2 - 20, y=20)

fen.update()


turn_label = tk.Label(fen, text="")
turn_label.place(x=20, y=20)

attacker_grid = Grid(attacker_canv, 10, placeable_ships={"Battleship": 1})
attacker_grid.trace(10)

ai_grid = AI_Grid(ai_canv, 10)
ai_grid.trace(10)

start_btn = tk.Button(fen, text='Démarrer', width=12, command=start_stop)
start_btn.place(x=400, y=board_size+120)
running = 0

quitBtn = tk.Button(fen, text='Fermer', width=12, command=fen.destroy)
quitBtn.place(x=500, y=board_size+120)

# pop_up("Instructions", instructions)

fen.mainloop()
