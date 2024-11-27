import batFramework as bf
import pygame
from .gameConstants import GameConstants as gconst
from .confirmScene import ask
from .mainStyle import decorate

class ImgButton(bf.Image,bf.ClickableWidget):...


class TitleScene(bf.Scene):
    def do_when_added(self):
        bf.AudioManager().load_music("main","audio/music/falling.mp3")
        bf.AudioManager().set_music_volume(0.1)
        bf.AudioManager().play_music("main",-1,3000)
        self.set_clear_color(gconst.CLAY)
        self.root.add(bf.Image("graphics/images/bg.png").set_padding(0).add_constraints(bf.FillX(),bf.FillY()))

        c = bf.Container(bf.Row(4).set_child_constraints(bf.MinWidth(60)))


        self.play_button = bf.Button("PLAY",lambda : self.manager.transition_to_scene("game",bf.transition.CircleOut(0.5,bf.easing.EASE_IN_OUT)))
        options_callback = lambda : self.manager.transition_to_scene("options",bf.transition.Fade(0.3))
        # o_b = ImgButton().from_surface(bf.ResourceManager().get_image("graphics/images/gear.png",True)).set_callback(options_callback)
        # o_b.set_unpressed_relief(0).set_pressed_relief(0).set_color((0,0,0,0))
        # self.root.add(o_b)
        # self.root.add(self.play_button)

        c.add(
            bf.Button("SETTINGS",options_callback),
            self.play_button,
            # bf.Button("QUIT",self.manager.stop)
            bf.Button("QUIT",lambda : ask(self.manager,"Quit the game :( ?",lambda v : self.manager.stop() if v else None))
        )
        c.add_constraints(bf.MarginBottom(8),bf.CenterX())
        c.set_draw_mode(bf.drawMode.SOLID).set_alpha(0)
        self.root.add(c)
        for child in c.children:
            child.set_autoresize_w(False)
            decorate(child)

        lb = bf.Label("-Baturay Turan-")
        lb.add_constraints(bf.AnchorBottomRight())
        lb.set_color((0,0,0,0)).disable_text_outline().set_padding(1)
        lb.set_text_color(bf.color.CLOUD)
        self.root.add(lb)
        self.root.focus_on(self.play_button)


        d = bf.Debugger()
        d.add_dynamic("hover",lambda : lb.rect.topleft)
        # d.add_dynamic("data",lambda : bf.AudioManager().musics )
        self.root.add(d)

    def do_on_enter(self):
        if self.manager.get_scene_at(1).name in ["options","confirm"]:
            return
        self.root.focus_on(self.play_button)

