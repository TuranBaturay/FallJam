import batFramework as bf
import pygame
from .gameConstants import GameConstants as gconst

class OptionsScene(bf.Scene):
    def do_when_added(self):
        self.set_clear_color(gconst.DARK_TREE)


    
