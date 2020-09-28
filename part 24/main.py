
import pygame as pg
import sys
from os import path
from settings import *
from sprites import *
from tilemap import *
from random import randint
import time
#from PIL import Image

#heads up display (HUD) functions

#what surfance we want to draw on, x, and y, andpercentage of health
def draw_player_health(surf, x, y, pct):
    if pct <0:
        pct =0
    BAR_LENGTH = 100
    BAR_HEIGHT = 20
    fill = pct * BAR_LENGTH
    outline_rect = pg.Rect(x,y,BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pg.Rect(int(x),int(y), int(fill), int(BAR_HEIGHT))
    if pct >0.6:
        col = GREEN
    elif pct > 0.3:
        col = YELLOW
    else:
        col = RED
    pg.draw.rect(surf, col, fill_rect)
    pg.draw.rect(surf,WHITE,outline_rect,2)

class Game:
    def __init__(self):
        #this is a setting to help reduce sound lag
        pg.mixer.pre_init(44100,-16,1,2048)
        #initialize game window
        # initaliaze pygame
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        # initialize mixer for sounds
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        #if you hold a buton for 500 milliseconds, program will repeat the key stroke
        #every 10th of a second. This allows for key press to respond to key held down
        pg.key.set_repeat(500,100)
        self.load_data()

    #draw text at a certain location. use align to instruct function what point x,y represent
    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        if align == "ne":
            text_rect.topright = (x, y)
        if align == "sw":
            text_rect.bottomleft = (x, y)
        if align == "se":
            text_rect.bottomright = (x, y)
        if align == "n":
            text_rect.midtop = (x, y)
        if align == "s":
            text_rect.midbottom = (x, y)
        if align == "e":
            text_rect.midright = (x, y)
        if align == "w":
            text_rect.midleft = (x, y)
        if align == "center":
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def load_data(self):
        game_folder = path.dirname(__file__)
        snd_folder = path.join(game_folder, 'snd')
        music_folder = path.join(game_folder, 'music')
        #self.map = Map(path.join(game_folder, 'map3.txt'))
        #having an issue with movnig the map file off the desktop
        self.available_weapons =['pistol']
        self.img_folder = path.join(game_folder, 'img')
        self.map_folder = 'C:\\Users\\Lee\\Desktop'
        #true type font, you can google for other fonts
        self.title_font = path.join(self.img_folder, 'ZOMBIE.TTF')
        self.hud_font = path.join(self.img_folder, 'Impacted2.0.TTF')
        #image to dim screen, crate a semi translucent recetange
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        #last parameter is translucency
        self.dim_screen.fill ((0,0,0,180))
        self.player_img = pg.image.load(path.join(self.img_folder,PLAYER_IMG)).convert_alpha()
        self.bullet_images = {}
        self.bullet_images['lg'] = pg.image.load(path.join(self.img_folder,BULLET_IMG)).convert_alpha()
        self.bullet_images['sm'] =pg.transform.scale(self.bullet_images['lg'],(10,10))
        self.mob_img = pg.image.load(path.join(self.img_folder, MOB_IMG)).convert_alpha()
        self.wall_img = pg.image.load(path.join(self.img_folder, WALL_IMG)).convert_alpha()
        #resize wall image to our tile size
        self.wall_img = pg.transform.scale(self.wall_img, (TILESIZE, TILESIZE))
        self.splat = pg.image.load(path.join(self.img_folder, SPLAT)).convert_alpha()
        #scale image
        self.splat = pg.transform.scale(self.splat, (64,64))
        self.gun_flashes = []
        for img in MUZZLE_FLASES:
            self.gun_flashes.append(pg.image.load(path.join(self.img_folder, img)).convert_alpha())
        self.blood_splat = []
        for img in BLOOD_SPLAT:
            #self.blood_splat.append(pg.transform.scale(pg.image.load(path.join(img_folder, img)).convert_alpha(),(10,10)))
            self.blood_splat.append(pg.image.load(path.join(self.img_folder, img)).convert_alpha())
        self.item_image = {}
        for item in ITEM_IMAGES:
            if item in['shotgun','machine_gun','sniper']:
                #resize
                self.item_image[item] = self.resize_image(ITEM_IMAGES[item], WEAPON_IMG_RESIZE)
            else: #don't resize
                self.item_image[item] = pg.image.load(path.join(self.img_folder, ITEM_IMAGES[item])).convert_alpha()
        #lighting effect
        self.fog = pg.Surface((WIDTH,HEIGHT))
        self.fog.fill(NIGHT_COLOR)

        self.light_mask = pg.image.load(path.join(self.img_folder,LIGHT_MASK)).convert_alpha()

        #resize
        #original code
        #self.light_mask = pg.transform.scale(self.light_mask, LIGHT_RADIUS)


        self.light_rect = self.light_mask.get_rect()
        #sound loading
        pg.mixer.music.load(path.join(music_folder, BG_MUSIC))
        #build a dictionary for effects
        self.effects_sounds = {}
        for type in EFFECTS_SOUNDS:
            self.effects_sounds[type] = pg.mixer.Sound(path.join(snd_folder, EFFECTS_SOUNDS[type]))
        #dictionary for weapon sounds
        #list for different sounds for each weapon
        self.weapon_sounds = {}
        for weapon in WEAPON_SOUNDS:
            self.weapon_sounds[weapon] = []
            for snd in WEAPON_SOUNDS[weapon]:
                s = pg.mixer.Sound(path.join(snd_folder,snd))
                s.set_volume(0.3)
                self.weapon_sounds[weapon].append(s)


        self.zombie_moan_sounds =[]
        for snd in ZOMBIE_MOAN_SOUNDS:
            #lower volumne
            s= pg.mixer.Sound(path.join(snd_folder, snd))
            #set_volume allows you to change from 0 to 1, with 1 being the current volume
            s.set_volume(0.1)
            self.zombie_moan_sounds.append(s)
        self.player_hit_sounds = []
        for snd in PLAYER_HIT_SOUNDS:
            self.player_hit_sounds.append(pg.mixer.Sound(path.join(snd_folder, snd)))
        self.zombie_hit_sounds = []
        for snd in ZOMBIE_HIT_SOUNDS:
            self.zombie_hit_sounds.append(pg.mixer.Sound(path.join(snd_folder, snd)))

    def resize_image(self, file_name, size):
        self.img = pg.image.load(path.join(self.img_folder, file_name)).convert_alpha()
        ix, iy = self.img.get_size()
        return pg.transform.scale(self.img, (int(ix * size), int(iy * size)))

    def new(self):
        #start a new game, create sprite groups, initialize camera

        #create a sprite group named all_sprites, create a group with layers
        #self.all_sprites = pg.sprite.Group()
        self.all_sprites = pg.sprite.LayeredUpdates()
        # create a sprite group named all walls
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()
        #my attempt
        self.map = TiledMap(path.join(self.map_folder, 'mymap.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        self.mute = False

        self.x =0
        self.y =0

        #this is the code for using text file maps
        #Load the map data, create walls and spawn player
        #enumrate shows the index number and the item value
        #row will be the index value of each line from the text file (and ultimately the y coordinate for the wall)
        #tiles will contain a whole row of data from the map
        '''
        for row, tiles in enumerate(self.map.data):
            #col will be the index value for each digit in  for the specifc row in the map file(and ultimatley the x coordinate for the wall)
            #tile contains the value of each cell in the map

            
            for col, tile in enumerate(tiles):
                if tile == '1':
                    #Create walls (ineresting how the class is called without assigning it an object)
                    #pass the class constructor the game, a col and row
                    Wall(self, col, row)
                if tile == 'M':
                    #spawn mob, pass the game, column and row
                    Mob(self, col, row)
                if tile == 'P':
                    #spawn player, pass the game, column and row
                    self.player = Player(self, col, row)
        '''
        #loop through tmx objects (defined in object layer)
        #the properties are a dictionary for each
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2, tile_object.y + tile_object.height/2)
            #the property .name is the value I defined in Tiled
            if tile_object.name == 'player':
                self.player = Player(self,obj_center.x,obj_center.y)
            if tile_object.name == 'zombie':
                Mob(self,obj_center.x, obj_center.y)
            if tile_object.name == 'wall':
                #spawn obstacles
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name in ['health','shotgun','machine_gun','sniper']:
                Item(self,obj_center,tile_object.name)
        #spawn camera
        self.camera = Camera(self.map.width, self.map.height)
        #add a boolean variable
        self.draw_debug = False
        self.paused = False
        self.night = False
        if not self.mute:
            self.effects_sounds['level_start'].play()

    def run(self):
        #game loop
        self.playing = True
        #play music, loops-1 means repeat
        if not self.mute:
            pg.mixer.music.play(loops=-1)
        while self.playing:
            #delta t "timestep of the game"
            #how much time the previous frame took
            #given in milliseconds, divide by 1000 to get it in seconds
            #if running at 60 FPS, it will be 60th of a second
            #but will change if there's lag
            self.dt= self.clock.tick(FPS)/1000
            self.events()
            if not self.paused:
                self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()


    def update(self):
        #game loop-update
        self.all_sprites.update()
        #update camera based on tracking player
        #could update the camera based on any sprite (e.g. a bullet being shot)
        self.camera.update(self.player)

        #gameover
        #p.s. length of the mob group is how to count spries
        if len(self.mobs) ==0:
            self.playing = False

        if self.player.weapon == 'sniper':
            self.x, self.y = RedDot(self, self.player.pos+ WEAPONS[self.player.weapon]['barrel_offset'].rotate(-self.player.rot), vec(1,0).rotate(-self.player.rot)).findEnd()

        #player hit items
        hits = pg.sprite.spritecollide(self.player, self.items, False)
        for hit in hits:
            if hit.type == 'health' and self.player.health < PLAYER_HEALTH:
                hit.kill()
                if not self.mute:
                    self.effects_sounds['health_up'].play()
                self.player.add_health(HEALTH_PACK_AMOUNT)
            if hit.type in ('shotgun','machine_gun','sniper'):
                hit.kill() #removes the item image
                self.available_weapons.append(hit.type)
                if not self.mute:
                    self.effects_sounds['gun_pickup'].play()
                self.player.weapon = hit.type
                # load weapon image and scale in half
                self.weapon_img = self.resize_image(WEAPONS[self.player.weapon]['image'], WEAPON_IMG_RESIZE)
                self.weapon = Weapon(self, self.player.rect.center)

                '''
                if hit.type == 'sniper':
                    self.light_mask = self.resize_image(SNIPER_LIGHT_MASK, SNIPER_LIGHT_RESIZE)
                    # rotate
                    self.light_mask = pg.transform.rotate(self.light_mask, self.player.rot)
                    # recenter
                    self.light_rect = self.light_mask.get_rect(center=self.light_rect.center)
                '''

        #mobs hit palyer
        hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            #70% of the time play a random hit sound
            if random() <0.7:
                if not self.mute:
                    choice(self.player_hit_sounds).play()
            self.player.health -= MOB_DAMAGE
            #mob stops breifly
            hit.vel = vec(0,0)
            if self.player.health < 0:
                self.playing= False

            # if player gets hits by zombie
            if hits:
                # knock player back a bit
                #vector rotated at rotation of mob that hit player
                self.player.hit()
                self.player.pos += vec(MOB_KNOCKBACK, 0).rotate(-hits[0].rot)

        #bullets dissapear when hit zombie
        #pygame doc: groupcollide(group1, group2, dokill1, dokill2,
        #returns a dictionary for members that collided, the key is the mob, the
        #values are all of the bullets that hit it
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for mob in hits:
            #hit.health -= WEAPONS[self.player.weapon]['damage'] * len(hits[hit]) #we can use this to count the number of bullets that hit it
            for bullet in hits[mob]:
                mob.health -= bullet.damage
                pos = bullet.pos + BLOOD_SPLAT_OFFSET.rotate(-self.player.rot)
                #draw splat on zombie at position of bullet 80% of time
                if randint(0,10) < 8:
                    BloodSplat(self, pos)
            #set velocity of mob to 0. Bullet stopping power
            mob.vel = vec(0,0)


    def draw_grid(self):
        #every 32 pixles
        for x in range(0, WIDTH, TILESIZE):
            #draw horizontal line
            pg.draw.line(self.screen,LIGHTGREY, (x,0), (x,HEIGHT))

        for y in range(0, HEIGHT, TILESIZE):
            #draw vertical line
            pg.draw.line(self.screen,LIGHTGREY, (0,y), (WIDTH,y))

    def render_fog(self):
        #draw the light mask (gradient) onto fog image
        self.fog.fill(NIGHT_COLOR)

        if self.player.weapon == 'sniper':
        #double size (for some reason resizing in GIMP was slowing down program too much)
            #resize
            self.light_mask= self.resize_image(SNIPER_LIGHT_MASK, SNIPER_LIGHT_RESIZE)
            #rotate
            self.light_mask = pg.transform.rotate(self.light_mask, self.player.rot)
            #recenter
            self.light_rect= self.light_mask.get_rect(center=self.light_rect.center)
        else:
            self.light_mask = pg.image.load(path.join(self.img_folder, LIGHT_MASK)).convert_alpha()
            self.light_rect = self.light_mask.get_rect()


        self.light_rect.center = self.camera.apply(self.player).center
        self.fog.blit(self.light_mask, self.light_rect)
        self.screen.blit(self.fog, (0,0), special_flags=pg.BLEND_MULT)

    def draw(self):
        #game loop-draw

        #for debugging, set caption to frame rate
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))

        #self.screen.fill(BGCOLOR)
        #draw map based on location of camera
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        #draw grid for troubleshooting
        #self.draw_grid()


        if self.player.weapon == 'sniper':
            #draw red dot scope for sniper

            #from the end of the players weapon
            start = vec(self.camera.apply(self.player).centerx, self.camera.apply(self.player).centery)
            start = start + WEAPONS['sniper']['barrel_offset'].rotate(-self.player.rot)

            #in the direction of the player's rotation
            end_point = vec(1, 0).rotate(-self.player.rot)
            end_point*=1000

            pg.draw.line(self.screen, RED, start, (start.x + end_point.x,start.y + end_point.y))

        for sprite in self.all_sprites:
            #draw health bars for mobs only
            if isinstance(sprite, Mob):
                sprite.draw_health()
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            if self.draw_debug:
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(sprite.hit_rect),1)
        if self.draw_debug:
            for wall in self.walls:
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(wall.rect),1)

        #draw rectangle around player for troublshooting
        #pg.draw.rect(self.screen, WHITE, self.camera.apply(self.player),2)
        #pg.draw.rect(self.screen, WHITE, self.player.hit_rect, 2)

        if self.night:
            self.render_fog()

        #HUD function
        draw_player_health(self.screen, 10,10,self.player.health / PLAYER_HEALTH)
        self.draw_text('Zombies: {}'.format(len(self.mobs)),self.hud_font, 30, WHITE, WIDTH-10,10, align='ne')
        if self.paused:
            #draw dim screen at 0,0
            self.screen.blit(self.dim_screen,(0,0))
            self.draw_text("Paused", self.title_font, 105, RED, int(WIDTH / 2), int(HEIGHT /2), align="center")
        # flip imaginary whiteboard- always last
        pg.display.flip()

    def events(self):
        #catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                #h key toggle draw debug
                if event.key == pg.K_h:
                    self.draw_debug = not self.draw_debug
                if event.key == pg.K_p:
                    self.paused = not self.paused
                if event.key == pg.K_n:
                    self.night = not self.night
                if event.key == pg.K_m:
                    self.mute = not self.mute
                if event.key == pg.K_t:
                    # if you only have a pistol do nothing. Otherwise...
                    if len(self.available_weapons) > 1:
                        #if the current weapon is the last available weapon
                        if self.available_weapons.index(self.player.weapon) == len(self.available_weapons) - 1:
                            #jump to the pistol
                            self.player.weapon = 'pistol'
                        else:
                            #otherwise jump to the next available weapon
                            self.player.weapon =self.available_weapons[self.available_weapons.index(self.player.weapon) +1]
                            self.weapon_img = self.resize_image(WEAPONS[self.player.weapon]['image'], WEAPON_IMG_RESIZE)
                            self.weapon = Weapon(self, self.player.rect.center)


    def show_start_screen(self):
        pass

    def show_go_screen(self):
        self.screen.fill(BLACK)
        self.draw_text("GAME OVER", self.title_font, 100, RED, WIDTH/2, HEIGHT/2, align='center')
        self.draw_text('Press a key to start', self.title_font, 75, WHITE, WIDTH/2, HEIGHT *3/4, align='center')
        pg.display.flip()
        #wait for key to get pressed
        self.wait_for_key()

    def wait_for_key(self):
        #start with fresh event que
        pg.event.wait()
        waiting = True
        while waiting:
            #do nothing
            self.clock.tick(FPS)
            #check for events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting=False
                    self.quit()
                #when player releases key
                if event.type == pg.KEYUP:
                    waiting = False



g = Game()
g.show_start_screen()

while True:
    g.new()
    g.run()
    g.show_go_screen()


