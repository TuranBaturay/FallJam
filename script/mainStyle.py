import pygame
import batFramework as bf
from math import cos
from types import MethodType
 

def draw_focused(self:bf.InteractiveWidget,camera:bf.Camera):
    delta = cos( pygame.time.get_ticks() / 100)
    pos = camera.world_to_screen_point(self.get_padded_rect().move(-4+delta,0).midleft)
    pygame.draw.circle(camera.surface,"white",pos,2)
    pygame.draw.circle(camera.surface,bf.color.ORANGE_SHADE,pos,3,1)
    r = self.rect.copy()
    # if isinstance(self,bf.Button):
    #     r.height -= self.relief
    #     r.bottom = self.rect.bottom
    # camera.surface.fill((40,40,40),camera.world_to_screen(r),special_flags=pygame.BLEND_ADD)



class MainStyle(bf.Style):
    def apply(self, w):
        if isinstance(w,bf.InteractiveWidget):
            w.draw_focused = MethodType(draw_focused,w)
        if isinstance(w,bf.Shape):
            w.set_padding(2)
            w.set_color(bf.color.ORANGE)
            w.set_outline_color(bf.color.ORANGE_SHADE)
            w.set_border_radius(2)
        if isinstance(w,bf.Container):
            w.set_color((0,0,0,0))
        if isinstance(w,bf.Label):
            w.enable_text_outline()
            w.set_text_outline_color((120,90,90))
            w.set_text_color(bf.color.CLOUD_SHADE)
        if isinstance(w,bf.Button):
            w.set_shadow_color(bf.color.ORANGE_SHADE)
