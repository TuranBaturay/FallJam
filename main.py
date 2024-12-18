
import batFramework as bf
import pygame

from script import * 
bf.init(
    # (640,480),
    (240,180),
    # (64,64),
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
        GameScene("game"),
        ConfirmScene(),
        EndScreen("endscreen")
    ).run()
    # bf.Manager(
    #     ConfirmScene()
    # ).run()
 