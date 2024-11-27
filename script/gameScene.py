import batFramework as bf
import pygame
import pygame.freetype
from .gameConstants import GameConstants as gconst
from math import ceil, cos, sin
import random
from .mainStyle import decorate
from typing import Generator

class FireFly(bf.Drawable):
    effect_surf = pygame.Surface((32,32))
    bf.utils.draw_spotlight(effect_surf,(100,100,155),(0,0,0),1,effect_surf.get_width()//2-2)
    def __init__(self,spawn:tuple[float,float]):
        super().__init__(size=(8,8),convert_alpha = True)
        self.spawn = spawn
        self.offset = self.spawn[0]*100+ self.spawn[1]*70 + pygame.time.get_ticks()*80
        self.add_tags("firefly")
        self.rect.center = self.spawn



    def draw(self,camera):
        self.rect.center = self.spawn
        if not camera.intersects(self.rect):
            return
        
        v1 = 4*cos((self.offset+ pygame.time.get_ticks())/200)
        v2 = 2*sin((self.offset*1.5+ pygame.time.get_ticks())/300)
        v3 = 8*sin((self.offset+ pygame.time.get_ticks())/800)
        v4 = 4*sin((self.offset*80+ pygame.time.get_ticks())/80)
        dx = v1+v2
        dy = v3+v4
        point = self.rect.move(dx,dy).center
        screen_point = camera.world_to_screen_point(point)
        pygame.draw.circle(camera.surface,"white",screen_point,4)
        camera.surface.blit(
            FireFly.effect_surf,
            (screen_point[0]-FireFly.effect_surf.get_width()//2,screen_point[1]-FireFly.effect_surf.get_height()//2),
            special_flags=pygame.BLEND_ADD
        
        )

class Tile:
    def __init__(self,index,height_delta:float = 0):
        self.index = index
        # self.height_delta:float = height_delta
        self.height_delta = height_delta
        self.surface = None
        self.set_index(index)
    def set_index(self,index:int) ->bool:
        tmp = bf.ResourceManager().get_image(f"graphics/tiles/cube{index}.png",True)
        if tmp:
            self.surface = tmp
            self.index = index
            return True    
        return False

    def __repr__(self):
        return f"Tile({self.index})"
    
    def save(self):
        return (self.index,self.height_delta)

class IsoLevel(bf.Drawable):
    def __init__(self,width,height):
        super().__init__()
        self.width = width
        self.height = height
        self.player : bf.Character = None
        self.tiles = [[None for _ in range(width)] for _ in range(height)]
        tmp = pygame.transform.scale2x(bf.ResourceManager().get_image("graphics/images/cloud1.png",True))
        self.cloud_surf = pygame.transform.scale2x(tmp)



    def save(self)->dict:
        data = {"width":self.width,"height":self.height,"tiles":{}}
        for y,row in enumerate(self.tiles):
            for x,tile in enumerate(row):
                data["tiles"][f"{x},{y}"] = tile.save() if tile is not None else None

        return data
    def load(self,data:dict):
        bckp = [self.width,self.height,self.tiles.copy()]
        try:

            self.width = data["width"]
            self.height = data["height"]
            self.tiles = self.tiles = [[None for _ in range(self.width)] for _ in range(self.height)]
            for index,tile in data["tiles"].items():
                x = int(index.split(",")[0])
                y = int(index.split(",")[1])
                self.tiles[y][x] = Tile(*tile)
        except KeyError:
            self.width,self.height,self.tiles = bckp

    def iterate(self)->Generator[tuple[tuple,Tile],None,None]:
        for diag in range(self.width + self.height - 1):  # Total number of diagonals
            for x in range(max(0, diag - self.height + 1), min(self.width, diag + 1)):
                y = diag - x
                value = self.tiles[y][x]
                yield ((x,y),value)



    def get_at(self,x,y)->Tile|None:
        if x < 0 or x >= self.width:return None
        if y < 0 or y >= self.height:return None
        return self.tiles[y][x]

    def set_at(self,x,y,tile:Tile):
        if x < 0 or x >= self.width:return
        if y < 0 or y >= self.height:return
        self.tiles[y][x]=tile



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
        cloud_surf =self.cloud_surf

        cloud_rect = cloud_surf.get_frect()

        for value in self.iterate():
            (x, y) , tile = value
            pos = self.grid_to_iso(x, y)

            # if (x == 0) :
            #     yield (bf.ResourceManager().get_image("graphics/images/cloud1.png",True),cloud_rect.move_to(topleft = camera.world_to_screen_point(self.grid_to_iso(x-3,y))))
            # if (y == 0) :
            #     yield (bf.ResourceManager().get_image("graphics/images/cloud1.png",True), cloud_rect.move_to(topleft = camera.world_to_screen_point(self.grid_to_iso(x,y-3))))


            # Yield tile surface and screen position
            if tile is not None:
                rect = pygame.FRect(0,0,*tile.surface.get_size())
                rect.midbottom = pos[0],pos[1]+tile.height_delta
                if camera.intersects(rect):
                    yield (tile.surface, camera.world_to_screen_point(rect.topleft))

            if player_round == (x, y):
                yield from self.player._my_draw(camera)

            # if (x == self.width-1) and x%2 == 0:
            #     yield (
            #         bf.ResourceManager().get_image("graphics/images/cloud1.png",True),
            #         cloud_rect.move_to(topleft = camera.world_to_screen_point(self.grid_to_iso(x+1,y)))
            #     )
            
            # if (y == self.height-1) and y%2 == 0:
            #     yield (
            #         bf.ResourceManager().get_image("graphics/images/cloud1.png",True),
            #         cloud_rect.move_to(topleft = camera.world_to_screen_point(self.grid_to_iso(x,y+1)))
            #     )




    def draw(self, camera):
        camera.surface.fblits(self.generate_draw_list(camera))

class Player(bf.Character):
    def __init__(self,level:IsoLevel):
        super().__init__()
        self.speed = 2
        self.actions = bf.DirectionalKeyControls()
        self.height = -0.7
        self.target_delta_height = 0
        self.delta_height = 0
        self.casting_spell = False
        self.max_spell = 3
        self.spell_timeout = bf.SceneTimer(1,self.end_spell,scene_name="game")
        self.spell_counter = 5
        # for a in self.actions:
        #     # a.set_instantaneous()
        #     if a.name == "up":
        #         a.replace_key_control(pygame.K_w,pygame.K_z)
        #     if a.name == "left":
        #         a.replace_key_control(pygame.K_a,pygame.K_q)
        
        # self.actions.add_actions(
        #     bf.Action("fly-up").add_key_control(pygame.K_8).set_holding(),
        #     bf.Action("fly-down").add_key_control(pygame.K_2).set_holding(),
        #     )

        self.grid_position = [2,2]
        self.level = level

    def set_height(self,height):
        self.height = height


    def do_setup_animations(self):

        def add_anim(state,name):
            anim = bf.Animation(state+"_"+name)
            anim.from_surface(bf.ResourceManager().get_image(f"graphics/tiles/player/{state}_{name}.png",True),(64,64))
            self.add_animation(anim)

        add_anim("idle","up")
        add_anim("idle","down")
        add_anim("idle","left")
        add_anim("idle","right")
        add_anim("idle","magic")

        self.set_animation("idle_right")



    def do_setup_states(self):
        self.state_machine.add_state(bf.State("idle"))
        self.state_machine.set_state("idle")

    def do_process_actions(self, event):
        self.actions.process_event(event)
    def do_reset_actions(self):
        self.actions.reset()
    def do_update(self, dt):
        self.velocity.update(0,0)

        if self.casting_spell:return
        if self.actions.is_active("left"):
            self.velocity.x -=1
        elif self.actions.is_active("right"):
            self.velocity.x += 1

        if self.velocity.x > 0: 
            self.set_animation("idle_right")
        elif self.velocity.x <0:
            self.set_animation("idle_left")

        if self.velocity:
            self.velocity.normalize_ip()
        self.velocity *= dt * self.speed

        self.move_by_check_collision(self.velocity.x,0)


        if self.actions.is_active("up") and not self.velocity.x:
            self.velocity.y -=1
        elif self.actions.is_active("down") and not self.velocity.x:
            self.velocity.y += 1        

        if self.velocity.y <0:
            self.set_animation("idle_up")
        elif self.velocity.y >0:
            self.set_animation("idle_down")

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
            self.center_to_tile()     
            return
        res = self.get_neighboring()
        collision_list = [None]
        if (bf.ResourceManager().get_sharedVar("collision") == True):
            collision_list.append(1)
        if any(v==None or (v.index in collision_list) for v in res):
            self.grid_position =  old_pos
            self.velocity.update(0,0)
        
            
        self.center_to_tile()     

    def get_neighboring(self)->list[Tile|None]:
        res = []
        for c in [(-0.5,0),(0,-0.5),(-0.5,-0.5),(0.1,0),(0,0.1),(0.1,0.1)]:
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
            iso_pos[0],
            iso_pos[1] -gconst.TILE_HEIGHT-16,
        )
        # self.rect.midbottom = iso_pos
        t = self.level.get_at(round(self.grid_position[0]),round(self.grid_position[1]))
        if t:
            if t.height_delta != self.target_delta_height:
                self.target_delta_height = t.height_delta
        else:
            self.target_delta_height = 0    
        self.delta_height += (self.target_delta_height - self.delta_height) / 20
        self.rect.move_ip(0,self.delta_height)

    def _my_draw(self,camera:bf.Camera):
        self.center_to_tile()
        yield (self.get_current_frame(), camera.world_to_screen_point(self.rect.topleft))
    def draw(self, camera):
        return
    
    def start_spell(self):
        if self.casting_spell == True:
            return False
        if self.spell_counter >0:
            self.spell_counter -=1
        else:
            return False
        self.spell_timeout.start()
        self.casting_spell = True
        self.old_anim = self.get_current_animation().name
        self.set_animation("idle_magic")
        return True
    
    def end_spell(self):
        self.casting_spell = False
        self.set_animation(self.old_anim)
class GameScene(bf.Scene):
    def do_when_added(self):
        
        
        
        
        self.do_blur  = False
        self.set_clear_color(gconst.CLAY)
        self.add_actions(
            *bf.DirectionalKeyControls(),
            bf.Action("back").add_key_control(pygame.K_ESCAPE),
            bf.Action("spawn").add_key_control(pygame.K_w),
            bf.Action("spell").add_key_control(pygame.K_SPACE),
            bf.Action("catch").add_key_control(pygame.K_a),

            bf.Action("tree").add_key_control(pygame.K_KP1),
            bf.Action("cube").add_key_control(pygame.K_KP2),
            bf.Action("raise").add_key_control(pygame.K_KP7).set_holding(),
            bf.Action("lower").add_key_control(pygame.K_KP4).set_holding(),
            bf.Action("toggle_collisions").add_key_control(pygame.K_KP9)

        )
        bf.ResourceManager().set_sharedVar("collision",False)

        self.level = IsoLevel(64,64)

        # Your IsoLevel instance

        width,height = self.level.width,self.level.height
        for y in range(height):
            for x in range(width):
                index = 1
                value = random.random()
                if value < 0.9:
                    index = 0
                self.level.set_at(x, y, Tile(index,random.randint(-4,4)))


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
        d.add_dynamic("tile",lambda : self.level.get_at(*[round(i) for i in self.player.grid_position]))
        d.add_dynamic("vel",lambda : [round(i,3) for i in self.player.velocity])
        d.add_dynamic("collisions",lambda : bf.ResourceManager().get_sharedVar("collision"))
        self.root.add(d)

        lb_fireflies = bf.Label(f"Fireflies {0}/{len(self.get_by_tags("firefly"))}")
        decorate(lb_fireflies)
        bf.SceneTimer(0.2,lambda : lb_fireflies.set_text(f"Fireflies {0}/{len(self.get_by_tags("firefly"))}"),True,"game").start()

        frame = bf.Shape().set_draw_mode(bf.drawMode.TEXTURED).set_texture(bf.ResourceManager().get_image("graphics/images/frame2.png",True)).add_constraints(bf.FillX(),bf.FillY())
        frame.add(lb_fireflies.add_constraints(bf.MarginLeft(4),bf.MarginTop(4)))
        self.root.add(frame)

        box = bf.Container(bf.RowFill(2)).add_constraints(bf.AnchorBottomRight())
        ti = bf.TextInput()
        box.add(
            ti,
            bf.Button("SAVE",lambda : self.save(ti.get_text())),
            bf.Button("LOAD",lambda : self.load(ti.get_text())),
        )
        frame.add(box)
        
        self.magic_row = bf.Container(bf.Row(2)).set_padding((8,4))
        self.magic_row.add_constraints(bf.AnchorTopRight())

        frame.add(self.magic_row)

    def save(self,path):
        print("save to : ",path)
        data = {"level":self.level.save(),"fireflies" : [f.spawn for f in self.get_by_tags("firefly")]}
        bf.ResourceManager().save_json_to_file(path+".json",data)

    def load(self,path):
        data = bf.ResourceManager().load_json_from_file(path+".json")
        for f in self.get_by_tags("firefly"):
            self.remove_world_entity(f)

        for f in data["fireflies"]:
            self.add_world_entity(FireFly(f))
        self.level.load(data["level"])

    def catch(self):
        bf.AudioManager().play_sound("firefly")
        

    def spell(self):
        if self.player.start_spell():
            bf.AudioManager().play_sound("spell")
            self.magic_row.remove(self.magic_row.children[-1])
        elif self.player.spell_counter <= 0:
            bf.ResourceManager().set_sharedVar("end_type","game_over")
            self.manager.transition_to_scene("endscreen")

    def do_update(self, dt):
        if self.actions.is_active("back"):
            self.manager.transition_to_scene("options",bf.transition.Fade(0.3))
        if self.actions.is_active("left"):
            self.camera.move_by(-60*dt,0)
        if self.actions.is_active("right"):
            self.camera.move_by(60*dt,0)
        if self.actions.is_active("up"):
            self.camera.move_by(0,-60*dt)
        if self.actions.is_active("down"):
            self.camera.move_by(0,60*dt)
        if self.actions.is_active("spawn"):
            f = FireFly(self.player.rect.midtop)
            self.add_world_entity(f)
        if self.actions.is_active("spell"):
            self.spell()
        if self.actions.is_active("catch"):
            self.catch()
        if self.actions.is_active("tree"):
            grid_pos = [round(i) for i in self.player.grid_position]
            self.level.set_at(*grid_pos,Tile(1,random.randint(-4,4)))
        if self.actions.is_active("cube"):
            grid_pos = [round(i) for i in self.player.grid_position]
            self.level.set_at(*grid_pos,Tile(0,random.randint(-4,4)))
        if self.actions.is_active("raise"):
            grid_pos = [round(i) for i in self.player.grid_position]
            t : Tile = self.level.get_at(*grid_pos)
            if t is None:
                return
            t.height_delta -=1
        if self.actions.is_active("lower"):
            grid_pos = [round(i) for i in self.player.grid_position]
            t : Tile = self.level.get_at(*grid_pos)
            if t is None:
                return
            t.height_delta +=1
        if self.actions.is_active("toggle_collisions"):
            bf.ResourceManager().set_sharedVar("collision",not bf.ResourceManager().get_sharedVar("collision"))

    def do_post_world_draw(self, surface):
        self.fx_surf.fill((0,0,0))
        bf.utils.draw_spotlight(self.fx_surf,(0,0,0), (255,255,255), 32,surface.get_height(),self.camera.world_to_screen_point(self.player.rect.center))
        tmp = pygame.transform.box_blur(self.fx_surf,1)
        surface.blit(tmp,(0,0),special_flags=pygame.BLEND_SUB)

    def do_final_draw(self, surface):
        return
        if self.do_blur > 0:
            tmp = surface.copy()
            pygame.transform.box_blur(tmp,round(self.do_blur),dest_surface=surface)
            self.do_blur-=0.1

    def do_on_enter_early(self):
        self.do_blur = 2
        if self.manager.get_scene_at(0).name == "title":
            self.init()
    def do_on_enter(self):
        self.do_blur = 0



    def init(self):
        self.player.grid_position = [1,1]
        # self.load("1.json")
        self.player.spell_counter = self.player.max_spell
        self.magic_row.add(*[bf.Image().from_path("graphics/images/magic.png").add_tags("magic") for _ in range(self.player.max_spell)])
        bf.ResourceManager().set_sharedVar("end_type","win")
        self.player.set_animation("idle_right")

