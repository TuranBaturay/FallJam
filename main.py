import batFramework as bf
import pygame
from types import MethodType
def draw_focused(self:bf.InteractiveWidget,camera:bf.Camera):
    pos = camera.world_to_screen_point(self.get_padded_rect().midleft)
    pygame.draw.circle(camera.surface,"white",pos,4,0,False,True,True,False)

class MainStyle(bf.Style):
    def apply(self, w):
        if isinstance(w,bf.InteractiveWidget):
            w.draw_focused = MethodType(draw_focused,w)
        if isinstance(w,bf.Shape):
            w.set_padding(1)
            w.set_color(bf.color.ORANGE)
            w.set_outline_color(bf.color.ORANGE_SHADE)
            w.set_border_radius(2)
        if isinstance(w,bf.Container):
            w.set_color((0,0,0,0))
        if isinstance(w,bf.Label):
            w.set_text_color(bf.color.CLOUD_SHADE)
        if isinstance(w,bf.Button):
            w.set_shadow_color(bf.color.ORANGE_SHADE)

class TitleScene(bf.Scene):
    def do_when_added(self):
        self.set_clear_color((100,50,60))
        c = bf.Container(bf.Column(2)).add_constraints(bf.MarginBottom(2),bf.MarginLeft(2))
        c.add(
            bf.Button("PLAY"),
            bf.Button("OPTIONS"),
            bf.Button("QUIT"),
        )
        self.root.add(c)


bf.init(
    (64,64),
    pygame.SCALED,
    default_font="fonts/batFont.ttf",
    default_font_size=8,
    resource_path="data",    
    fps_limit=60
)

bf.StyleManager().add(MainStyle())
bf.Manager(TitleScene("title")).run()