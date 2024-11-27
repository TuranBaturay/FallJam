import batFramework as bf
import pygame
from typing import Callable,Any
from .mainStyle import decorate



class ConfirmScene(bf.Scene):
    def __init__(self):
        # super().__init__("confirm", True, True)
        super().__init__("confirm", False, True)
        # self.camera = bf.Camera(pygame.SRCALPHA,bf.const.RESOLUTION,True)
        # self.hud_camera = bf.Camera(pygame.SRCALPHA,bf.const.RESOLUTION,True)
        
    def do_on_enter_early(self):
        super().do_on_enter_early()
        self.manager.get_scene_at(0).set_visible(True)
        self.buttons[0].get_focus()
    def do_when_added(self):
        # self.set_clear_color((0,0,0,1))
        c = bf.Container(bf.Column(2).set_child_constraints(bf.FillX())).add_constraints(bf.PercentageWidth(0.5))
        sub = bf.Container(bf.RowFill(2))
        c.add_constraints(bf.Center())
        self.label = bf.Label("Confirm ?").add_constraints(bf.FillX())
        c.add(self.label,sub)
        self.root.add(c)
        self.callback : Callable[[bool],Any]= lambda val : None
        self.buttons = [
            bf.Button("NO",lambda : self.__internal(False)),bf.Button("YES",lambda : self.__internal(True))
        ]
        sub.add(*self.buttons)
        self.buttons[1].get_focus()
        for w in [*self.buttons,self.label]:
            decorate(w)

    def __internal(self,value):
        self.callback(value)
        s = self.manager.get_scene_at(1)
        if not s : 
            return
        
        self.manager.transition_to_scene(s.name)


    # def do_early_draw(self, surface):
        # surface.fill((10,10,10),special_flags=pygame.BLEND_SUB)

def ask(manager:bf.Manager,string:str,callback:Callable[[bool],Any]):
    s : ConfirmScene = manager.get_scene("confirm")
    s.label.set_text(string)
    s.callback = callback
    manager.transition_to_scene("confirm")
