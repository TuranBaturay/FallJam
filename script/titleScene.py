import batFramework as bf
import pygame
from .gameConstants import GameConstants as gconst

class TitleScene(bf.Scene):
    def do_when_added(self):
        self.set_clear_color(gconst.CLAY)
        self.root.add(bf.Image("graphics/images/autumn.png").set_padding(0))
        c = bf.Container(bf.Column(2)).add_constraints(bf.MarginBottom(4),bf.MarginLeft(4))
        c.add(
            bf.Button("PLAY",lambda : self.manager.transition_to_scene("game",bf.transition.Fade(0.3))),
            bf.Button("OPTIONS",lambda : self.manager.transition_to_scene("options",bf.transition.Fade(0.3))),
            bf.Button("QUIT"),
        )
        self.root.add(c)

        lb = bf.Label("-Baturay Turan-").add_constraints(bf.AnchorBottomRight())
        lb.set_color((0,0,0,0)).disable_text_outline().set_padding(1)
        lb.set_text_color(bf.color.ORANGE)
        self.root.add(lb)
        self.play_button = c.children[0]
        self.root.focus_on(self.play_button)


    def do_on_enter(self):
        if self.manager.get_scene_at(1).name == "options":return
        self.root.focus_on(self.play_button)