import batFramework as bf
import pygame
from .gameConstants import GameConstants as gconst
from .mainStyle import decorate


class EndScreen(bf.Scene):
    def do_when_added(self):
        
        self.set_clear_color((0,0,0))


    def do_on_enter_early(self):
        if bf.ResourceManager().get_sharedVar("end_type") == "game_over":
            self.game_over()
        else:
            self.you_win()

    def do_when_added(self):
        c = bf.Container(bf.Column(2).set_child_constraints(bf.FillX()))
        self.main = c
        self.root.add(c)

    def you_win(self):
        self.main.clear_children()
        sub = bf.Container(bf.RowFill(2))
        self.main.add_constraints(bf.Center(),bf.PercentageWidth(0.7))
        self.label = bf.Label("YOU WIN !").add_constraints(bf.FillX())
        self.main.add(self.label,sub)
        self.buttons = [bf.Button("MAIN MENU",lambda : self.manager.transition_to_scene("title")),bf.Button("QUIT",self.manager.stop)]
        sub.add(*self.buttons)
        self.buttons[1].get_focus()
        for w in [*self.buttons,self.label]:
            decorate(w)
    def game_over(self):
        self.main.clear_children()
        self.main.clear_children()
        sub = bf.Container(bf.RowFill(2))
        self.main.add_constraints(bf.Center(),bf.PercentageWidth(0.7))
        self.label = bf.Label("GAME OVER").add_constraints(bf.FillX())
        self.main.add(self.label,sub)
        self.buttons = [bf.Button("MAIN MENU",lambda : self.manager.transition_to_scene("title")),bf.Button("QUIT",self.manager.stop)]
        sub.add(*self.buttons)
        self.buttons[1].get_focus()
        for w in [*self.buttons,self.label]:
            decorate(w)