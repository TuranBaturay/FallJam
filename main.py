import batFramework as bf
import pygame

from script import OptionsScene,TitleScene,MainStyle


bf.init(
    (240,180),
    pygame.SCALED,
    default_font="fonts/batFont.ttf",
    default_font_size=8,
    resource_path="data",    
    fps_limit=60
)

bf.StyleManager().add(MainStyle())

if __name__ == "__main__":
    bf.Manager(
        TitleScene("title"),    
        OptionsScene("options"),    
    ).run()
