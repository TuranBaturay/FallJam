import batFramework as bf
import pygame
from .gameConstants import GameConstants as gconst
from .mainStyle import decorate

class OptionsScene(bf.Scene):

    def do_on_enter_early(self):
        if self.manager.get_scene_at(0).name =="game":
            self.main_menu_button.enable()
        else:
            self.main_menu_button.disable()

    def do_when_added(self):
        self.set_clear_color((45,21,37))
        # self.root.add(bf.Image("graphics/images/bg.png").set_padding(0).add_constraints(bf.FillX(),bf.FillY()))

        c = bf.Container(bf.Column(2).set_child_constraints(bf.FillX()))

        slider = bf.Slider("MUSIC",0.1)
        slider.set_range(0,1)
        slider.set_step(0.1)
        slider.set_modify_callback(bf.AudioManager().set_music_volume)
        self.main_menu_button = bf.Button("Main Menu",lambda:self.manager.transition_to_scene("title"))
        
        decorate(self.main_menu_button)
        c.add(
            bf.Button("BACK",lambda : self.manager.transition_to_scene(self.manager.get_scene_at(1).name,bf.transition.Fade(0.3))),
            slider,
            bf.Toggle("FULLSCREEN",lambda val: pygame.display.toggle_fullscreen()),
            self.main_menu_button
        )

        c.add_constraints(bf.MarginBottom(4),bf.MarginLeft(4))
        self.root.add(c)
        self.root.focus_on(c.children[0])
        self.container = c
        for child in c.children:
            decorate(child)
    
        self.root.add(bf.Image("graphics/images/controls.png",True).add_constraints(bf.MarginRight(4),bf.MarginTop(4)))

