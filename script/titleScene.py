import batFramework as bf
import pygame
from .gameConstants import GameConstants as gconst

class TitleScene(bf.Scene):
    def do_when_added(self):
        self.set_clear_color((100,50,60))
        c = bf.Container(bf.Column(2)).add_constraints(bf.MarginBottom(4),bf.MarginLeft(4))
        c.add(
            bf.Button("PLAY"),
            bf.Button("OPTIONS"),
            bf.Button("QUIT"),
        )
        self.root.add(c)
