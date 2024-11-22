import batFramework as bf
import pygame
from .gameConstants import GameConstants as gconst

class ImgButton(bf.Image,bf.ClickableWidget):...


class TitleScene(bf.Scene):
    def do_when_added(self):
        self.set_clear_color(gconst.CLAY)
        self.root.add(bf.Image("graphics/images/autumn.png").set_padding(0))
        self.play_button = bf.Button("PLAY",lambda : self.manager.transition_to_scene("game",bf.transition.Fade(0.3)))
        self.play_button.add_constraints(bf.PercentageWidth(0.6))
        self.root.add(self.play_button)
        options_callback = lambda : self.manager.transition_to_scene("options",bf.transition.Fade(0.3))
        o_b = ImgButton().from_surface(bf.ResourceManager().get_image("graphics/images/gear.png",True)).set_callback(options_callback)
        o_b.set_unpressed_relief(0).set_pressed_relief(0).set_color((0,0,0,0))
        self.root.add(o_b)

        lb = bf.Label("-Baturay Turan-").add_constraints(bf.AnchorBottom())
        lb.set_color((0,0,0,0)).disable_text_outline().set_padding(1)
        lb.set_text_color(bf.color.CLOUD)
        self.root.add(lb)
        self.root.focus_on(self.play_button)


    def do_on_enter(self):
        if self.manager.get_scene_at(1).name == "options":return
        self.root.focus_on(self.play_button)