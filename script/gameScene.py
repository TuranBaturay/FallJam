import batFramework as bf
import pygame
from .gameConstants import GameConstants as gconst
from math import ceil
import random
import numpy as np

def generate_simple_3d_noise(width, height, depth, scale=0.1, seed=None):
    """
    Generate 3D noise manually without external libraries.

    Args:
        width (int): Width of the noise array.
        height (int): Height of the noise array.
        depth (int): Depth of the noise array.
        scale (float): Scale factor for noise (affects smoothness).
        seed (int | None): Seed for random number generator.

    Returns:
        np.ndarray: 3D array of noise values.
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    noise_data = np.zeros((width, height, depth), dtype=np.float32)

    for z in range(depth):
        for y in range(height):
            for x in range(width):
                # Generate pseudo-random noise, scaled by coordinates
                noise_value = (
                    random.uniform(0, 1)
                    * (np.sin(x * scale) + np.cos(y * scale) + np.sin(z * scale))
                )
                noise_data[x, y, z] = noise_value

    return noise_data



class Tile:
    def __init__(self,index):
        self.index = index
class IsoLevel(bf.Drawable):
    def __init__(self,width,height,depth):
        super().__init__()
        self.width = width
        self.height = height
        self.depth = depth
        self.player : bf.Character = None
        self.tiles = [[{} for _ in range(width)] for _ in range(height)]
        self.tile_surf = img = bf.ResourceManager().get_image("graphics/tiles/cube.png",True)


    def iterate(self):
        for z in range(self.depth,-1,-1):
            for diag in range(self.width + self.height - 1):  # Total number of diagonals
                for x in range(max(0, diag - self.height + 1), min(self.width, diag + 1)):
                    y = diag - x
                    try :
                        value = self.tiles[y][x][z]
                        yield ((x,y,z),value)
                    except KeyError:
                        continue



    def get_at(self,x,y,z):
        if x < 0 or x >= self.width:return
        if y < 0 or y >= self.height:return
        if z in self.tiles[y][x]:
            return self.tiles[y][x][z]
        else :
            return None

    def set_at(self,x,y,z,tile_index):
        if x < 0 or x >= self.width:return
        if y < 0 or y >= self.height:return
        self.tiles[y][x][z]=Tile(tile_index)



    def get_debug_outlines(self):
        yield None

    def iso_to_world(self,x, y, z):
        screen_x = (x - y) * gconst.TILE_WIDTH // 2
        screen_y = (x + y) * gconst.TILE_HEIGHT // 2 - z * gconst.TILE_HEIGHT
        return screen_x, screen_y

    def grid_to_iso(self,x, y, height):
        tile_width = gconst.TILE_WIDTH
        tile_height = gconst.TILE_HEIGHT
        screen_x = (x - y) * (tile_width // 2)
        screen_y = (x + y) * (tile_height // 2) - height * tile_height
        return screen_x, screen_y

    def iterate(self):
        for z in range(self.depth):
            for diag in range(self.width + self.height - 1):  # Total number of diagonals
                for x in range(max(0, diag - self.height + 1), min(self.width, diag + 1)):
                    y = diag - x
                    if z not in self.tiles[y][x]:
                        continue
                    yield ((x,y,z),self.tiles[y][x][z])

    def generate_draw_list(self, camera: bf.Camera):
        """
        Generate a draw list optimized to avoid drawing tiles completely obscured by others.

        Args:
            camera (bf.Camera): The camera to transform world coordinates to screen coordinates.

        Yields:
            tuple: (surface, screen_position) for visible tiles.
        """
        player_round = round(self.player.grid_position[0]), round(self.player.grid_position[1])
        max_depth = self.depth - 1

        for value in self.iterate():
            (x, y, z), tile = value

            # Skip if there are tiles above that completely cover this one
            if z < max_depth and any(k > z for k in self.tiles[y][x].keys()):
                continue

            # Convert grid position to isometric screen position
            pos = self.grid_to_iso(x, y, z)

            # Yield tile surface and screen position
            yield (self.tile_surf, camera.world_to_screen_point(pos))

            if player_round == (x, y):
                # Ensure there are tiles at the current (x, y)
                top_z = max(self.tiles[y][x].keys(), default=-1)  # Default to -1 if no tiles
                if self.player.grid_position[2] >= top_z-1:
                    yield from self.player._my_draw(camera)


    def generate_draw_list_with_info(self, camera: bf.Camera):
        """
        Generate a draw list optimized to avoid drawing tiles completely obscured by others.

        Args:
            camera (bf.Camera): The camera to transform world coordinates to screen coordinates.

        Yields:
            tuple: (surface, screen_position) for visible tiles.
        """
        player_drawn = False
        player_round = round(self.player.grid_position[0]), round(self.player.grid_position[1]),round(self.player.grid_position[2])
        max_depth = self.depth - 1

        for value in self.iterate():
            (x, y, z), tile = value

            # Skip if there are tiles above that completely cover this one
            # if z < max_depth and any(k > z for k in self.tiles[y][x].keys()):
            #     continue

            # Convert grid position to isometric screen position
            pos = self.grid_to_iso(x, y, z)

            # Yield tile surface and screen position
            yield (self.tile_surf, camera.world_to_screen_point(pos),(x,y,z))

            if player_round[:2] == (x, y) :
                # yield (self.tile_surf, camera.world_to_screen_point(pos),(x,y,z))
                # Ensure there are tiles at the current (x, y)
                # top_z = max(self.tiles[y][x].keys(), default=-1)  # Default to -1 if no tiles
                # if player_round[2] >= top_z-1:
                if not player_drawn:
                    val = next(self.player._my_draw(camera))
                    player_drawn= True
                    yield (*val,(x,y,z))

    def draw(self, camera):
        # print("-" * 30)
        # Generate the draw list with additional information (tile, position, z-value).
        draw_list = list(self.generate_draw_list_with_info(camera))

        # Sort the tiles by z-layer (ascending).
        draw_list.sort(key=lambda val: val[2][2])  # Sort by the z-value.

        for val in draw_list:
            tile_surface, position, z_value = val

            # Apply shadow effect for this z-layer.
            camera.surface.fill((1, 1, 1), special_flags=pygame.BLEND_RGB_SUB)

            # Draw the tile.
            camera.surface.blit(tile_surface, position)

            # Debug output to verify z-layer drawing order.
            # print(z_value)

class Player(bf.Character):
    def __init__(self,level:IsoLevel):
        super().__init__()
        self.speed = 8#1.3
        self.actions = bf.WASDControls()
        self.height = -0.7
        for a in self.actions:
            # a.set_instantaneous()
            if a.name == "up":
                a.replace_key_control(pygame.K_w,pygame.K_z)
            if a.name == "left":
                a.replace_key_control(pygame.K_a,pygame.K_q)
        
        self.actions.add_actions(
            bf.Action("fly-up").add_key_control(pygame.K_KP8).set_holding(),
            bf.Action("fly-down").add_key_control(pygame.K_KP2).set_holding(),
            )

        self.grid_position = [0,0,0]
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
        if self.actions.is_active("up"):
            self.grid_position[1] = max(0,self.grid_position[1]-self.speed*dt)
        if self.actions.is_active("down"):
            self.grid_position[1] = min(self.level.height-1,self.grid_position[1] + self.speed*dt)
        if self.actions.is_active("left"):
            self.grid_position[0] = max(0,self.grid_position[0]-self.speed*dt)
        if self.actions.is_active("right"):
            self.grid_position[0] = min(self.level.width-1,self.grid_position[0] + self.speed*dt)
        if self.actions.is_active("fly-up"):
            self.grid_position[2] +=self.speed*dt
        if self.actions.is_active("fly-down"):
            self.grid_position[2] -=self.speed*dt
        self.rect.midbottom = self.level.grid_to_iso(*self.grid_position[:2],self.grid_position[2]+self.height)
        self.rect.move_ip(gconst.TILE_WIDTH//2,gconst.TILE_HEIGHT//2 - 16)

    
    def _my_draw(self,camera:bf.Camera):
        self.rect.midbottom = self.level.grid_to_iso(*self.grid_position[:2],self.grid_position[2]+self.height)
        self.rect.move_ip(gconst.TILE_WIDTH//2,gconst.TILE_HEIGHT//2 - 16)
        yield (self.get_current_frame(),camera.world_to_screen_point(self.rect.topleft))
        # camera.surface.blit(self.get_current_frame(),camera.world_to_screen_point(self.rect.topleft))

    def draw(self, camera):
        pass

class GameScene(bf.Scene):
    def do_when_added(self):
        self.set_clear_color(gconst.CLAY)
        self.add_actions(bf.Action("back").add_key_control(pygame.K_ESCAPE),*bf.DirectionalKeyControls())
        self.level = IsoLevel(20,20,5)


        # Assuming noise_array_normalized is the generated 3D noise array
        noise_array_normalized = generate_simple_3d_noise(20, 20, 5, scale=0.1, seed=42)
        noise_array_normalized = (noise_array_normalized - noise_array_normalized.min()) / (noise_array_normalized.max() - noise_array_normalized.min())

        # Your IsoLevel instance

        # # Iterate over the 3D noise array and call set_at
        width, height, depth = noise_array_normalized.shape
        for z in range(depth):
            for y in range(height):
                for x in range(width):
                    # Use the noise value as the "value" for set_at
                    value = noise_array_normalized[x, y, z]
                    if value < 0.5:
                        self.level.set_at(x, y, z, 0)



        self.add_world_entity(self.level)
        self.player  = Player(self.level)
        self.level.player = self.player
        self.camera.set_follow_point_func(lambda :self.player.rect.center)
        self.camera.set_follow_speed(0.8)
        self.camera.set_follow_damping(2)
        self.camera.zoom_by(-0.5)
        self.add_world_entity(self.player)
        self.camera.set_center(*self.player.rect.center)
        self.fx_surf = pygame.Surface(self.camera.rect.size)
        




        bf.Timer(1,lambda : print("Hello pygame-ce"),True).start()


        d = bf.BasicDebugger()
        d.add_dynamic("grid",lambda : [int(i) for i in self.player.grid_position])
        self.root.add(d)
        # self.root.add(bf.Slider("height",0).set_range(-5,5).add_constraints(bf.AnchorTopRight()).set_modify_callback(self.player.set_height))
        

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


    def do_post_world_draw(self, surface):
        pass
        # self.fx_surf.fill((0,0,0))
        # bf.utils.draw_spotlight(self.fx_surf,(0,0,0), (200,200,200), 64,surface.get_height(),self.camera.world_to_screen_point(self.player.rect.center))
        # tmp = pygame.transform.box_blur(self.fx_surf,1)
        # surface.blit(tmp,(0,0),special_flags=pygame.BLEND_SUB)
        # self.level.get_indicators(self.camera)
        # for val in self.level.indicators:
        #     pos,color = val
        #     pygame.draw.circle(surface,color,(pos[0]+gconst.TILE_WIDTH//2,pos[1]+gconst.TILE_HEIGHT//2),6)