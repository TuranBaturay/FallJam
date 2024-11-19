import batFramework as bf
import pygame
from .gameConstants import GameConstants as gconst

class OptionsScene(bf.Scene):
    def do_when_added(self):
        self.set_clear_color(gconst.CLAY)

        c = bf.Container(bf.Column(2))
        c.add(
            bf.Button("Back",lambda : self.manager.transition_to_scene(self.manager.get_scene_at(1).name,bf.transition.Fade(0.3))),
            bf.Toggle("Fullscreen",lambda val: pygame.display.toggle_fullscreen())
        )

        c.add_constraints(bf.MarginBottom(4),bf.MarginLeft(4))
        self.root.add(c)
        self.root.focus_on(c.children[0])

    
