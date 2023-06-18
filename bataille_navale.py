import tkinter as tk


# class Grid:
#     def __init__(self):
#         pass


class Battleship:
    def __init__(self, length: int, orientation: int, master_coord: tuple, img=None, img_hor=None, tag=None):
        self.length = length
        self.ori = orientation
        # master_coord = (x, y)
        self.m_coord = master_coord
        self.is_dead = 0
        self.hp = length
        self.tag = tag
        self.img = img
        self.img_hor = img_hor
        self.coords = {}
        for i in range(self.length):
            if self.ori == 0:  # horizontal
                self.coords[(self.m_coord[0]+i, self.m_coord[1])] = 1
            elif self.ori == 1:  # vertical
                self.coords[(self.m_coord[0], self.m_coord[1]+i)] = 1

    def rotate(self, ships):
        if self.ori == 0:
            self.ori = 1
        elif self.ori == 1:
            self.ori = 0
        coords = {}
        for i in range(self.length):
            if self.ori == 0:
                coords[(self.m_coord[0]+i, self.m_coord[1])] = 1
            elif self.ori == 1:
                coords[(self.m_coord[0], self.m_coord[1]+i)] = 1
        test = 0
        for i in list(coords):
            for y in ships:
                if i in y:
                    test = 1
                    if self.ori == 0:
                        self.ori = 1
            if not(0 <= i[0] <= 9):
                test = 1
                if self.ori == 0:
                    self.ori = 1
            elif not(0 <= i[1] <= 14):
                test = 1
                if self.ori == 1:
                    self.ori = 0
        if test == 0:
            self.coords = coords

    def place(self, master_coord, ships):
        self.m_coord = master_coord
        coords = {}
        for i in range(self.length):
            if self.ori == 0:
                coords[(self.m_coord[0]+i, self.m_coord[1])] = 1
            elif self.ori == 1:
                coords[(self.m_coord[0], self.m_coord[1]+i)] = 1
        test = 0
        for i in list(coords):
            for y in ships:
                if i in y:
                    test = 1
            if not(0 <= i[0] <= 9) or not(0 <= i[1] <= 14):
                test = 1
        if test == 0:
            self.coords = coords

    def hit(self):
        self.hp -= 1
        if self.hp == 0:
            self.is_dead = 1


class Officer:
    def __init__(self, name):
        self.warships = 5
        self.name = name

    def defeat(self, opponent):
        if self.warships == 0:
            return(f"{self.name} lost the battle. {opponent.name} won.")
        return("")


class Game:
    def __init__(self, phase):
        self.phase = phase
