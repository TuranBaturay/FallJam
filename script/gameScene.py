import batFramework as bf
import pygame
from .gameConstants import GameConstants as gconst
from math import ceil, cos, sin
import random



class FireFly(bf.Drawable):
    def __init__(self,spawn:tuple[float,float]):
        super().__init__(size=(8,8),convert_alpha = True)
        self.spawn = spawn
        # pygame.draw.circle(self.surface,"white",(4,4),4)


    def draw(self,camera):
        if not camera.intersects(self.rect):
            return
        point = self.rect.move(4*cos(pygame.time.get_ticks()/200),0).center
        pygame.draw.circle(camera.surface,"white",camera.world_to_screen_point(point),4)

class Tile:
    def __init__(self,index,height_delta:float = 0):
        self.index = index
        self.height_delta:float = height_delta
        
class IsoLevel(bf.Drawable):
    def __init__(self,width,height):
        super().__init__()
        self.width = width
        self.height = height
        self.player : bf.Character = None
        self.tiles = [[None for _ in range(width)] for _ in range(height)]
        self.tile_surf = img = bf.ResourceManager().get_image("graphics/tiles/cube.png",True)

    def iterate(self):
        for diag in range(self.width + self.height - 1):  # Total number of diagonals
            for x in range(max(0, diag - self.height + 1), min(self.width, diag + 1)):
                y = diag - x
                value = self.tiles[y][x]
                yield ((x,y),value)



    def get_at(self,x,y):
        if x < 0 or x >= self.width:return
        if y < 0 or y >= self.height:return
        return self.tiles[y][x]

    def set_at(self,x,y,tile_index):
        if x < 0 or x >= self.width:return
        if y < 0 or y >= self.height:return
        self.tiles[y][x]=Tile(tile_index,random.randint(-2,2))



    def get_debug_outlines(self):
        yield None

    def iso_to_world(self,x, y, z):
        screen_x = (x - y) * gconst.TILE_WIDTH // 2
        screen_y = (x + y) * gconst.TILE_HEIGHT // 2 - z * gconst.TILE_HEIGHT
        return screen_x, screen_y

    def grid_to_iso(self,x, y):
        tile_width = gconst.TILE_WIDTH
        tile_height = gconst.TILE_HEIGHT
        screen_x = (x - y) * (tile_width // 2)
        screen_y = (x + y) * (tile_height // 2) 
        return screen_x, screen_y


    def generate_draw_list(self, camera: bf.Camera):
        """
        Generate a draw list optimized to avoid drawing tiles completely obscured by others.

        Args:
            camera (bf.Camera): The camera to transform world coordinates to screen coordinates.

        Yields:
            tuple: (surface, screen_position) for visible tiles.
        """
        player_round = (
            round(self.player.grid_position[0]),
            round(self.player.grid_position[1]),
        )

        for value in self.iterate():
            (x, y) , tile = value
            pos = self.grid_to_iso(x, y)

            # Yield tile surface and screen position
            if tile:
                new_pos = (pos[0],pos[1]+tile.height_delta)
                if camera.intersects((*new_pos,gconst.TILE_WIDTH,gconst.TILE_HEIGHT)):
                    yield (self.tile_surf, camera.world_to_screen_point(new_pos))

            if player_round == (x, y):
                yield from self.player._my_draw(camera)



    def draw(self, camera):
        camera.surface.fblits(self.generate_draw_list(camera))

class Player(bf.Character):
    def __init__(self,level:IsoLevel):
        super().__init__()
        self.speed = 2
        self.actions = bf.WASDControls()
        self.height = -0.7
        for a in self.actions:
            # a.set_instantaneous()
            if a.name == "up":
                a.replace_key_control(pygame.K_w,pygame.K_z)
            if a.name == "left":
                a.replace_key_control(pygame.K_a,pygame.K_q)
        
        self.actions.add_actions(
            bf.Action("fly-up").add_key_control(pygame.K_8).set_holding(),
            bf.Action("fly-down").add_key_control(pygame.K_2).set_holding(),
            )

        self.grid_position = [2,2]
        self.level = level

    def set_height(self,height):
        self.height = height

    def do_setup_animations(self):
        anim = bf.Animation("idle")
        anim.from_surface(bf.ResourceManager().get_image("graphics/tiles/player.png",True),(64,64))
        self.add_animation(anim)
        self.set_animation("idle")

    def do_setup_states(self):
        self.state_machine.add_state(bf.State("idle"))
        self.state_machine.set_state("idle")

    def do_process_actions(self, event):
        self.actions.process_event(event)
    def do_reset_actions(self):
        self.actions.reset()
    def do_update(self, dt):
        self.velocity.update(0,0)

        
        if self.actions.is_active("left"):
            self.velocity.x -=1
        elif self.actions.is_active("right"):
            self.velocity.x += 1

        if self.velocity:
            self.velocity.normalize_ip()
        self.velocity *= dt * self.speed

        self.move_by_check_collision(self.velocity.x,0)


        if self.actions.is_active("up") and not self.velocity.x:
            self.velocity.y -=1
        elif self.actions.is_active("down") and not self.velocity.x:
            self.velocity.y += 1        

        if self.velocity:
            self.velocity.normalize_ip()
        self.velocity *= dt * self.speed
        
        self.move_by_check_collision(0,self.velocity.y)
        
        
    def move_by_check_collision(self,x,y):
        old_pos = self.grid_position.copy()
        self.grid_position[0] +=x
        self.grid_position[1] +=y

        val = self.level.get_at(*[round(i) for i in self.grid_position])
        if val is None:
            self.grid_position =  old_pos
            self.velocity.update(0,0)
        res = self.get_neighboring()
        if any(v ==None for v in res):
            self.grid_position =  old_pos
            self.velocity.update(0,0)
            
        self.center_to_tile()     

    def get_neighboring(self)->list[Tile|None]:
        res = []
        for c in [(-0.25,0),(0,-0.25),(0.25,0),(0.25,0.25)]:
            res.append(
                self.level.get_at(
                    round(self.grid_position[0]+c[0]),
                    round(self.grid_position[1]+c[1])
                )
            )
        return res
       
    def center_to_tile(self):
        iso_pos = self.level.grid_to_iso(*self.grid_position)
        self.rect.midbottom = (
            iso_pos[0] + gconst.TILE_WIDTH //2,
            iso_pos[1] +gconst.TILE_HEIGHT-16,
        )

    def _my_draw(self,camera:bf.Camera):
        self.center_to_tile()
        # screen_pos = camera.world_to_screen_point((
        #     self.rect.centerx,
        #     self.rect.bottom + self.height * gconst.TILE_HEIGHT
        # ))
        yield (self.get_current_frame(), camera.world_to_screen_point(self.rect.topleft))
    def draw(self, camera):
        return

class GameScene(bf.Scene):
    def do_when_added(self):
        self.set_clear_color(gconst.CLAY)
        self.add_actions(
            bf.Action("back").add_key_control(pygame.K_ESCAPE),*bf.DirectionalKeyControls(),
            bf.Action("spawn").add_key_control(pygame.K_SPACE),

        )
        self.level = IsoLevel(20,20)

        # Your IsoLevel instance

        width = height = 64
        for y in range(height):
            for x in range(width):
                value = random.random()
                if value < 0.8:
                    self.level.set_at(x, y, 0)


        self.add_world_entity(self.level)
        self.player  = Player(self.level)
        self.level.player = self.player
        self.camera.set_follow_point_func(lambda :self.player.rect.center)
        self.camera.set_follow_speed(1)
        self.camera.set_follow_damping(10)
        # self.camera.zoom_by(-0.5)
        self.add_world_entity(self.player)
        self.camera.set_center(*self.player.rect.center)
        self.fx_surf = pygame.Surface(self.camera.rect.size)
        

        d = bf.FPSDebugger()
        d.add_dynamic("grid",lambda : [round(i) for i in self.player.grid_position])
        d.add_dynamic("vel",lambda : [round(i,3) for i in self.player.velocity])
        self.root.add(d)

        lb_fireflies = bf.Label(f"{0}/{10}")
        self.root.add(lb_fireflies)
        

    def add_firefly(self,firefly):
        self.add_world_entity(firefly)

    def do_update(self, dt):
        if self.actions.is_active("back"):
            self.manager.transition_to_scene("title",bf.transition.Fade(0.3))

        if self.actions.is_active("left"):
            self.camera.move_by(-60*dt,0)
        if self.actions.is_active("right"):
            self.camera.move_by(60*dt,0)
        if self.actions.is_active("up"):
            self.camera.move_by(0,-60*dt)
        if self.actions.is_active("down"):
            self.camera.move_by(0,60*dt)
        if self.actions.is_active("spawn"):
            self.add_firefly(FireFly(self.player.rect.center))


    def do_post_world_draw(self, surface):
        return
        self.fx_surf.fill((0,0,0))
        bf.utils.draw_spotlight(self.fx_surf,(0,0,0), (200,200,200), 64,surface.get_height(),self.camera.world_to_screen_point(self.player.rect.center))
        tmp = pygame.transform.box_blur(self.fx_surf,1)
        surface.blit(tmp,(0,0),special_flags=pygame.BLEND_SUB)
