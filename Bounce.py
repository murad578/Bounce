import sys; import pygame
#This is a convention to import pygame constants, such as keys.
from pygame.locals import *
#This is used to import tilemap loading system (tilemaps are created in a program called Tiled and are stored as tmx).
from pytmx.util_pygame import load_pygame

class Button():
    """Class that sets up buttons based on the given parameters."""
    def __init__(self, text, group, order=2, type='center', base_color=(255,255,255), hovering_color=(234,50,60), top_color=(61,61,61)):
        self.text=text
        self.group=group; self.group.append(self)
        self.order=order
        self.pos_y=10+self.order*40
        self.width=len(self.text)*12+12; self.height=32
        if type=='center': self.pos_x=(256-self.width)//2; self.top_rect=pygame.Rect((self.pos_x, self.pos_y), (self.width, self.height)) 
        if type=='left': self.pos_x=20; self.top_rect=pygame.Rect((self.pos_x, self.pos_y), (self.width, self.height))
        if type=='right': self.pos_x=256-20-self.width; self.top_rect=pygame.Rect((self.pos_x, self.pos_y), (self.width, self.height))
        self.base_color=base_color; self.hovering_color=hovering_color; self.top_color=top_color
        self.text_color=base_color
        self.text_surf=font.render(self.text, False, self.text_color)
        self.text_rect=self.text_surf.get_rect(center=self.top_rect.center)
        self.pressed=False; self.mouse_on=False; self.current=False; self.hover=False
    def press(self):
        mouse_pos=pygame.mouse.get_pos()
        self.mouse_on=self.top_rect.collidepoint(mouse_pos)
        checked=False
        if self.mouse_on or self.current:
            self.text_color=self.hovering_color
            if not self.hover: play_sound('data/sfx/button_hover.wav'); self.hover=True
            #It is checked if the alt key is pressed or not for the button press (enter) to not collide with the alternative Fullscreen On/Off shortuct alt+enter.
            if pygame.mouse.get_pressed()[0] or (keys[K_RETURN] and not alt_pressed) or keys[K_SPACE]: self.pressed=True
            elif self.pressed:
                if game_state.button!=None: game_state.button_group[game_state.button].current=False; game_state.button=None
                if self.text=='Play': game_state.previous_state=game_state.state; game_state.state='level_menu'
                if self.text=='Continue': game_state.previous_state=game_state.state; game_state.state='main_game'
                if self.text=='Quit': pygame.quit(); sys.exit()
                if self.text=='Main Menu': game_state.previous_state=game_state.state; game_state.state='main_menu'
                if self.text=='Options': game_state.previous_state=game_state.state; game_state.state='options_menu'
                if self.text=='Fullscreen off': screen=pygame.display.set_mode((256, 192), pygame.SCALED | pygame.FULLSCREEN); self.text='Fullscreen on'; checked=True
                if self.text=='Fullscreen on' and not checked: screen=pygame.display.set_mode((256, 192), pygame.SCALED); self.text='Fullscreen off'
                if self.text=='Sound off': self.text='Sound on'; checked=True
                if self.text=='Sound on' and not checked: self.text='Sound off'
                if self.text=='Music off': self.text='Music on'; pygame.mixer.music.play(loops=-1); checked=True
                if self.text=='Music on' and not checked: self.text='Music off'; pygame.mixer.music.stop()
                if self.text=='Back': game_state.previous_state, game_state.state=game_state.state, game_state.previous_state
                if self.text.isdigit(): game_state.current_level=Level(self.text); game_state.previous_state=game_state.state; game_state.state='main_game'
                play_sound('data/sfx/button_press.wav')
                self.pressed=False
        else: self.text_color=self.base_color; self.mouse_on=False; self.current=False; self.hover=False
    def update(self):
        self.press()
        self.text_surf=font.render(self.text, False, self.text_color)
        self.text_rect=self.text_surf.get_rect(center=self.top_rect.center)
        pygame.draw.rect(screen, self.top_color, self.top_rect)
        screen.blit(self.text_surf, self.text_rect)

class GameState():
    """Top-level class. Almost everything is controlled from here, and this is the only class run in the main while loop."""
    def __init__(self):
        self.state='main_menu'
        #The previous state is stored to provide more flexibility in state transitions.
        self.previous_state=self.state
        self.current_level=None
        self.go_back=False
        self.button=None; self.button_group=None; self.mouse_on_button=False; self.button_move=False
    #Game states and their respective actions and button groups.
    def main_menu(self):
        self.button_group=main_menu_buttons
        screen.blit(pygame.image.load('data/images/background_1.png').convert_alpha(),(0,0))
    def options_menu(self):
        self.button_group=options_buttons
        if keys[K_ESCAPE] or keys[K_BACKSPACE]: self.go_back=True
        elif self.go_back: self.state_change(); self.previous_state, self.state=self.state, self.previous_state; self.go_back=False
        screen.blit(pygame.image.load('data/images/background_2.png').convert_alpha(),(0,0))
    def esc_menu(self):
        self.button_group=esc_menu_buttons
        if keys[K_ESCAPE] or keys[K_BACKSPACE]: self.go_back=True
        elif self.go_back: self.state_change(); self.previous_state=self.state; self.state='main_game'; self.go_back=False
        screen.fill((0,205,249))
        self.current_level.camera_group.custom_draw()
    def level_menu(self):
        self.button_group=level_menu_buttons
        if keys[K_ESCAPE] or keys[K_BACKSPACE]: self.go_back=True
        elif self.go_back: self.state_change(); self.previous_state, self.state=self.state, self.previous_state; self.go_back=False
        screen.blit(pygame.image.load('data/images/background_2.png').convert_alpha(),(0,0))
    def main_game(self):
        self.button_group=None
        if keys[K_ESCAPE] or keys[K_BACKSPACE]: self.go_back=True
        elif self.go_back: self.state_change(); self.previous_state=self.state; self.state='esc_menu'; self.go_back=False
        screen.fill((0,205,249))
        self.current_level.camera_group.update(); self.current_level.camera_group.custom_draw()
    def button_state(self):
        """Function that checks for the state of the buttons (whether the mouse cursor is on a button or not; which button is currently selected)."""
        if self.button_group!=None:
            self.mouse_on_button=False
            for button in self.button_group:
                button.update()
                if button.mouse_on:
                    if self.button!=None: self.button_group[self.button].current=False; self.button=None
                    self.mouse_on_button=True
            #This sets the key scheme to control the current button with the keyboard (if the mouse cursor isn't on any button) and modular arithmetic is used to determine the next button.
            if not self.mouse_on_button:
                if self.state!='level_menu':
                    if self.button==None:
                        if keys[K_DOWN] or keys[K_s]: self.next_button=0; self.button_move=True
                        if keys[K_UP] or keys[K_w]: self.next_button=len(self.button_group)-1; self.button_move=True
                        if not (keys[K_DOWN] or keys[K_s] or keys[K_UP] or keys[K_w]) and self.button_move: self.button=self.next_button; self.button_group[self.button].current=True; self.button_move=False
                    else:
                        if keys[K_DOWN] or keys[K_s]: self.next_button=(self.button+1)%len(self.button_group); self.button_move=True
                        if keys[K_UP] or keys[K_w]: self.next_button=(self.button-1)%len(self.button_group); self.button_move=True
                        if not (keys[K_DOWN] or keys[K_s] or keys[K_UP] or keys[K_w]) and self.button_move: self.button_group[self.button].current=False; self.button=self.next_button; self.button_group[self.button].current=True; self.button_move=False
                else:
                    if self.button==None:
                        if keys[K_DOWN] or keys[K_s] or keys[K_RIGHT] or keys[K_d]: self.next_button=0; self.button_move=True
                        if keys[K_UP] or keys[K_w] or keys[K_LEFT] or keys[K_a]: self.next_button=len(self.button_group)-1; self.button_move=True
                        if not (keys[K_DOWN] or keys[K_s] or keys[K_RIGHT] or keys[K_d] or keys[K_UP] or keys[K_w] or keys[K_LEFT] or keys[K_a]) and self.button_move: self.button=self.next_button; self.button_group[self.button].current=True; self.button_move=False
                    else:
                        if keys[K_RIGHT] or keys[K_d]: self.next_button=(self.button+1)%len(self.button_group); self.button_move=True
                        if keys[K_DOWN] or keys[K_s]: self.next_button=(self.button+3+(int(self.button>=len(self.button_group)-4))-2*int(self.button==len(self.button_group)-1 or self.button==len(self.button_group)-3))%len(self.button_group)%len(self.button_group); self.button_move=True
                        if keys[K_LEFT] or keys[K_a]: self.next_button=(self.button-1)%len(self.button_group); self.button_move=True
                        if keys[K_UP] or keys[K_w]: self.next_button=(self.button-3-(int(self.button<=2))+2*int(self.button==1)+int(self.button==len(self.button_group)-1))%len(self.button_group); self.button_move=True
                        if not (keys[K_DOWN] or keys[K_s] or keys[K_RIGHT] or keys[K_d] or keys[K_UP] or keys[K_w] or keys[K_LEFT] or keys[K_a]) and self.button_move: self.button_group[self.button].current=False; self.button=self.next_button; self.button_group[self.button].current=True; self.button_move=False
    def state_change(self):
        if self.button!=None: self.button_group[self.button].current=False; self.button=None
    def state_manager(self):
        """Function that checks the game state to run the respective state."""
        if self.state=='main_menu': self.main_menu()
        if self.state=='options_menu': self.options_menu()
        if self.state=='level_menu': self.level_menu()
        if self.state=='esc_menu': self.esc_menu()
        if self.state=='main_game': self.main_game()
        self.button_state()

class CameraGroup(pygame.sprite.Group):
    """Class that is used to control camera in the main game state based on the player position."""
    def __init__(self):
        super().__init__()
        self.display_surface=pygame.display.get_surface()
        self.offset=pygame.math.Vector2(-50,-30)
        self.half_w=self.display_surface.get_size()[0]//2
        self.half_h=self.display_surface.get_size()[1]//2
        self.camera_borders={'left': 80, 'right': 80, 'top': 48, 'bottom': 48}
        l=self.camera_borders['left']
        t=self.camera_borders['top']
        w=self.display_surface.get_size()[0]-self.camera_borders['left']-self.camera_borders['right']
        h=self.display_surface.get_size()[1]-self.camera_borders['top']-self.camera_borders['bottom']
        self.camera_rect=pygame.Rect(l,t,w,h)
    def custom_draw(self):
        """Function that draws sprites with an offset based on the player's position."""
        if game_state.current_level.ball.rect.left<self.camera_rect.left: self.camera_rect.left=game_state.current_level.ball.rect.left
        if game_state.current_level.ball.rect.right>self.camera_rect.right: self.camera_rect.right=game_state.current_level.ball.rect.right
        if game_state.current_level.ball.rect.top<self.camera_rect.top: self.camera_rect.top=game_state.current_level.ball.rect.top
        if game_state.current_level.ball.rect.bottom>self.camera_rect.bottom: self.camera_rect.bottom=game_state.current_level.ball.rect.bottom
        self.offset.x=-(self.camera_rect.left-self.camera_borders['left'])
        self.offset.y=-(self.camera_rect.top-self.camera_borders['top'])
        for sprite in self.sprites():
            offset_pos=sprite.rect.topleft+self.offset
            self.display_surface.blit(sprite.image, offset_pos)
        screen.blit(pygame.image.load('data/images/hp.png').convert_alpha(),(10,10))
        screen.blit((font_small.render(str(game_state.current_level.ball.hp),False,(255,255,255))), (20,5))
        screen.blit(pygame.image.load('data/images/sp.png').convert_alpha(),(10,25))
        screen.blit((font_small.render(str(game_state.current_level.ball.sp),False,(255,255,255))), (20,20))

class Level():
    """Class that is used to set up levels."""
    def __init__(self, level):
        self.level_data=load_pygame('data/maps/level_'+level+'.tmx', pixelalpha=True)
        #Necessary solitary sprite groups are created.
        for group in ['foreground', 'rubber', 'water', 'gate', 'pass', 'save', 'saved', 'hp', 'sizeup', 'sizedown', 'score', 'small_score', 'obstacle']:
            setattr(self, f'{group}_group', pygame.sprite.Group())
        #Sprites are created based on whether they are contained in tile/object groups, their type and their name in the tilemap tmx file and are placed in their solitary groups.
        for layer in self.level_data.visible_layers:
            if hasattr(layer,'data'):
                for x,y,surf in layer.tiles():
                    pos=(x*16, y*16)
                    Tile(pos=pos, surf=surf, group=getattr(self, f'{layer.name.lower()}_group'))
        sp=0
        for obj in self.level_data.objects:
            pos=(obj.x, obj.y); frames=None
            if hasattr(obj, 'frames') and obj.frames: frames=obj.frames
            if obj.type=='Start_point': self.ball=Ball(pos=pos, size=obj.name, sp=sp)
            elif obj.type=='Score':
                Object(obj, pos=pos, frames=frames, group=self.score_group); sp+=1
                if obj.name=='Small_score': Object(obj, pos=pos, frames=frames, group=self.small_score_group)
            else: Object(obj, pos=pos, frames=frames, group=getattr(self, f'{obj.type.lower().replace('_', '')}_group'))
        #Necessary composite sprite groups are created, and their respective solitary sprite groups are placed in them.
        self.collide_group=pygame.sprite.Group(); self.camera_group=CameraGroup()
        self.collide_group.add(self.foreground_group.sprites(), self.rubber_group.sprites(), self.gate_group.sprites(), self.sizeup_group.sprites(), self.sizedown_group.sprites())
        if self.ball.size=='big': self.collide_group.add(self.small_score_group.sprites())
        self.camera_group.add(self.water_group.sprites(), self.rubber_group.sprites(), self.foreground_group.sprites(), self.gate_group.sprites(), self.save_group.sprites(),  self.hp_group.sprites(), self.sizeup_group.sprites(), self.sizedown_group.sprites(), self.score_group.sprites(), self.obstacle_group.sprites(), self.ball)

class Tile(pygame.sprite.Sprite):
    """Tile class."""
    def __init__(self, pos, surf, group):
        super().__init__(group)
        self.image=surf
        self.rect=self.image.get_rect(topleft=pos)
        self.mask=pygame.mask.from_surface(self.image)

class Object(pygame.sprite.Sprite):
    """Class for almost every sprite other than tiles and the ball."""
    def __init__(self, obj, pos, frames, group):
        super().__init__(group)
        self.obj=obj
        self.pos=pos
        self.frames=frames
        self.current_frame_index=0
        self.time_since_last_frame=0
        self.frame_duration=None
        self.image=self.obj.image
        self.rect=self.image.get_rect(topleft=self.pos)
        self.mask=pygame.mask.from_surface(self.image)
        self.speed=1
    def move(self):
        #The only moving object in the game is an obstacle called 'Saw'.
        if self.obj.name=='Saw':
            self.rect.y+=self.speed
            if pygame.sprite.spritecollide(self, game_state.current_level.collide_group, False, pygame.sprite.collide_mask): self.rect.y-=self.speed; self.speed=-self.speed
    def animate(self):
        if self.frames!=None:
            #Animation frame duration management is maintained by the game fps.
            self.frame_duration=self.frames[self.current_frame_index].duration
            self.time_since_last_frame+=dt
            if self.time_since_last_frame>=self.frame_duration:
                self.time_since_last_frame=0
                self.current_frame_index=(self.current_frame_index+1)%len(self.frames)
                self.frame_duration=self.frames[self.current_frame_index].duration
                self.image=game_state.current_level.level_data.get_tile_image_by_gid(self.frames[self.current_frame_index].gid)
    def update(self):
        self.move()
        self.animate()

class Ball(pygame.sprite.Sprite):
    """Player class."""
    def __init__(self, pos, size, sp):
        super().__init__()
        self.size=self.save_size=size
        self.image=pygame.image.load('data/images/'+self.size+'_ball.png').convert_alpha()
        self.rect=self.image.get_rect(topleft=pos)
        self.mask=pygame.mask.from_surface(self.image)
        self.save_pos=pos
        self.hp=3; self.sp=sp
        self.speed=0; self.max_speed=4
        self.def_med_gravity_mag=12; self.def_big_gravity_mag=14
        self.gravity=0; self.gravity_mag=getattr(self, f'def_{self.size}_gravity_mag')
        self.jump=False; self.gravity_up=False; self.into_water=False; self.left=False; self.right=False
    #image_change and size_change functions are oftenly used actions in game mechanics.
    def image_change(self, img): self.image=pygame.image.load(img).convert_alpha(); self.rect=self.image.get_rect(bottomleft=self.rect.bottomleft); self.mask=pygame.mask.from_surface(self.image)
    def size_change(self, size):
        self.size=size; self.gravity_mag=getattr(self, f'def_{self.size}_gravity_mag'); self.image_change('data/images/'+self.size+'_ball.png')
        if self.size=='med': game_state.current_level.collide_group.remove(game_state.current_level.small_score_group.sprites())
        if self.size=='big': game_state.current_level.collide_group.add(game_state.current_level.small_score_group.sprites())
    #Game mechanics.
    def collides(self): return pygame.sprite.spritecollide(self, game_state.current_level.collide_group, False, pygame.sprite.collide_mask)
    def rubber_col(self): return pygame.sprite.spritecollide(self, game_state.current_level.rubber_group, False, pygame.sprite.collide_mask)
    def in_water(self): return pygame.sprite.spritecollide(self, game_state.current_level.water_group, False, pygame.sprite.collide_mask)
    def collide_repair(self):
        """Funtion that is used to repair the ball-tile/object collision in exceptional cases (for example, when the ball size up in a smaller space than the big ball's dimensions, it will get stuck in a tile/object) by modifying the ball's position and checking for the collision."""
        def repair(movx, movy):
            self.rect.x+=-movx; self.rect.y+=-movy
            while self.collides(): self.rect.x+=movx/abs(movx) if movx!=0 else 0; self.rect.y+=movy/abs(movy) if movy!=0 else 0
        mov=1
        while self.collides():
            self.rect.x+=-mov
            if not self.collides(): repair(-mov, 0); continue
            self.rect.x+=2*mov
            if not self.collides(): repair(mov, 0); continue
            self.rect.x+=-mov; self.rect.y+=-mov
            if not self.collides(): repair(0, -mov); continue
            self.rect.y+=2*mov
            if not self.collides(): repair(0, mov); continue
            self.rect.x+=-mov; self.rect.y+=-2*mov
            if not self.collides(): repair(-mov, -mov); continue
            self.rect.x+=2*mov
            if not self.collides(): repair(mov, -mov); continue
            self.rect.y+=2*mov
            if not self.collides(): repair(mov, mov); continue
            self.rect.x+=-2*mov
            if not self.collides(): repair(-mov, mov); continue
            self.rect.x+=mov; self.rect.y-=mov; mov+=1
    def save(self):
        for sprite in game_state.current_level.save_group:
                if pygame.sprite.collide_mask(self, sprite):
                    self.save_pos=sprite.pos; self.save_size=self.size
                    for new_sprite in game_state.current_level.saved_group:
                        if new_sprite.pos==sprite.pos: game_state.current_level.camera_group.add(new_sprite)
                    sprite.kill(); play_sound('data/sfx/save.wav')
    def heal(self):
        if pygame.sprite.spritecollide(self, game_state.current_level.hp_group, True, pygame.sprite.collide_mask): self.hp+=1; play_sound('data/sfx/hp.wav')
    def size_up(self):
        if pygame.sprite.spritecollide(self, game_state.current_level.sizeup_group, False, pygame.sprite.collide_mask) and self.size=='med':
            self.size_change('big'); play_sound('data/sfx/size_up.wav')
    def size_down(self):
        if pygame.sprite.spritecollide(self, game_state.current_level.sizedown_group, False, pygame.sprite.collide_mask) and self.size=='big':
            self.size_change('med'); play_sound('data/sfx/size_down.wav')
    def score(self):
        if pygame.sprite.spritecollide(self, game_state.current_level.score_group, True, pygame.sprite.collide_mask): self.sp-=1; play_sound('data/sfx/score.wav')
        if self.sp==0:
            for sprite in game_state.current_level.gate_group: sprite.kill()
            for sprite in game_state.current_level.pass_group: game_state.current_level.camera_group.add(sprite)
    def damage(self):
        if pygame.sprite.spritecollide(self, game_state.current_level.obstacle_group, False, pygame.sprite.collide_mask): self.size_change(self.save_size); self.rect.x, self.rect.y=self.save_pos; self.hp-=1; play_sound('data/sfx/damage.wav')
        if self.hp==0: game_state.previous_state='main_menu'; game_state.state='level_menu'
    def level_pass(self):
        if pygame.sprite.spritecollide(self, game_state.current_level.pass_group, False, pygame.sprite.collide_mask): game_state.previous_state='main_menu'; game_state.state='level_menu'; play_sound('data/sfx/pass.wav')
    #Some clever mathematics and variable/file name manipulation is used in the funtions player_input and apply_gravity to avoid extensive if/elif/else statements and make the program more efficient.
    def player_input(self):
        """Function that checks player input and updates the ball's x position and the jumping state."""
        self.left=False; self.right=False
        if (keys[K_SPACE] or keys[K_UP] or keys[K_w]) and not self.jump: self.gravity=-self.gravity_mag; self.jump=True; play_sound('data/sfx/ball_jump.wav')
        if keys[K_LEFT] or keys[K_a]: self.speed+=-1+self.speed//(-self.max_speed); self.left=True
        if keys[K_RIGHT] or keys[K_d]: self.speed+=1-self.speed//self.max_speed; self.right=True
        if self.speed!=0 and not ((keys[K_LEFT] or keys[K_a]) or (keys[K_RIGHT] or keys[K_d])): self.speed+=-1*(self.speed//abs(self.speed))
        for _ in range(abs(self.speed)):
                self.rect.x+=self.speed//abs(self.speed)
                if self.collides():
                    self.size_up(); self.size_down()
                    self.rect.x-=self.speed//abs(self.speed)
                    self.left=self.right=False
                    self.speed=0
                    break
    def apply_gravity(self):
        """Function that updates the ball's y position."""
        self.gravity+=1
        if self.size=='big' and self.in_water():
            self.gravity=-5
            if not self.into_water: play_sound('data/sfx/into_water.wav'); self.into_water=True
        else: self.into_water=False
        if self.gravity!=0:
            self.jump=True
            for _ in range(abs(self.gravity)):
                self.rect.y+=self.gravity//abs(self.gravity)
                if self.collides():
                    self.size_up(); self.size_down()
                    if self.rubber_col():
                        if not self.gravity_up: self.gravity_mag=int(self.gravity_mag*1.5); self.gravity_up=True
                        else: self.gravity_mag=getattr(self, f'def_{self.size}_gravity_mag')
                    else: self.gravity_mag=getattr(self, f'def_{self.size}_gravity_mag'); self.gravity_up=False
                    self.rect.y-=self.gravity//abs(self.gravity); self.jump=bool(-(-0.5+0.5*(self.gravity//abs(self.gravity)))); self.gravity=0
                    self.image_change('data/images/'+self.size+'_ball.png')
                    break
            else: self.image_change('data/images/'+self.size+'_ball_air_'+str((int(self.right)-int(self.left))*(self.gravity//abs(self.gravity)))+'.png'); self.gravity_up=False
    def update(self):
        """Function that checks game mechanics with their respective functions and updates them."""
        self.player_input()
        self.apply_gravity()
        self.collide_repair()
        self.save()
        self.heal()
        self.score()
        self.damage()
        self.level_pass()

#This is the initation of the pygame and setup of the game environment (such as display, time, font, sound) and an instance of the conroller class GameState.
pygame.init()
screen=pygame.display.set_mode((256, 192), pygame.SCALED)
pygame.display.set_caption('Bounce')
pygame.display.set_icon(pygame.image.load('data/images/icon.png').convert_alpha())
display=pygame.Surface((256,192))
game_state=GameState()
clock=pygame.time.Clock()
font=pygame.font.Font('data/fonts/font.ttf', 24)
font_small=pygame.font.Font('data/fonts/font.ttf', 16)
pygame.mixer.init()
pygame.mixer.music.load('data/sfx/music.wav'); pygame.mixer.music.play(loops=-1)
def play_sound(sound):
    if button_sound.text=='Sound on': pygame.mixer.Sound(sound).play()
alt_pressed=False

#Button groups and buttons are set up.
main_menu_buttons=[]; options_buttons=[]; level_menu_buttons=[]; esc_menu_buttons=[]
button_play=Button('Play', group=main_menu_buttons, order=0, type='center')
button_main_options=Button('Options', group=main_menu_buttons, order=1, type='center')
button_main_quit=Button('Quit', group=main_menu_buttons, order=2, type='center')    
button_continue=Button('Continue', group=esc_menu_buttons, order=0, type='left')
button_esc_options=Button('Options', group=esc_menu_buttons, order=1, type='left')
button_main_menu=Button('Main Menu', group=esc_menu_buttons, order=2, type='left')
button_esc_quit=Button('Quit', group=esc_menu_buttons, order=3, type='left')
button_fullscreen=Button('Fullscreen off', group=options_buttons, order=0, type='center')
button_sound=Button('Sound on', group=options_buttons, order=1, type='center')
button_music=Button('Music on', group=options_buttons, order=2, type='center')
button_back_options=Button('Back', group=options_buttons, order=3, type='center')
button_1=Button('1', group=level_menu_buttons, order=1.5, type='left')
button_2=Button('2', group=level_menu_buttons, order=1.5, type='center')
button_3=Button('3', group=level_menu_buttons, order=1.5, type='right')
button_back_level=Button('Back', group=level_menu_buttons, order=3, type='center')
#The main while loop.
while True:
    keys=pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type==QUIT: pygame.quit(); sys.exit()
        #This sets the function keys shortcuts: F2=Sound On/Off, F3=Music On/Off, F11=Fullscreen On/Off (alternatively alt+enter).
        if event.type==pygame.KEYDOWN:
            if event.key==K_RALT: alt_pressed=True
        if event.type==pygame.KEYUP:
            if event.key==K_F2:
                if button_sound.text=='Sound off': button_sound.text='Sound on'
                else: button_sound.text='Sound off'
            if event.key==K_F3:
                if button_music.text=='Music off': button_music.text='Music on'; pygame.mixer.music.play(loops=-1)
                else: button_music.text='Music off'; pygame.mixer.music.stop()
            if event.key==K_F11 or (event.key==K_RETURN and alt_pressed):
                if button_fullscreen.text=='Fullscreen off': screen=pygame.display.set_mode((256, 192), pygame.SCALED | pygame.FULLSCREEN); button_fullscreen.text='Fullscreen on'
                else: screen=pygame.display.set_mode((256, 192), pygame.SCALED); button_fullscreen.text='Fullscreen off'
            if event.key==K_RALT: alt_pressed=False
    game_state.state_manager()
    pygame.display.update()
    #The fps is stored as a variable to be used in animation frame duration, and currently is set to 60 fps for a smooth gameplay (can be changed according to needs).
    dt=clock.tick(60)