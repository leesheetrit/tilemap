import pygame as pg
vec = pg.math.Vector2


#define colors
WHITE = (255,255,255)
BLACK = (0,0,0)
DARKGREY = (40,40,40)
LIGHTGREY = (100,100,100)
GREEN = (0,255,0)
RED = (255,0,0)
YELLOW = (255, 255,0)
BROWN = (106, 55, 5)
CYAN = (0, 255, 255)


#Game options/settings
WIDTH = 1024 #16* 64 or 32*32 or 64*16
HEIGHT = 768 #16*48 or 32 * 24 or 64*12
FPS = 60
TITLE = "Tilemap Demo"
BGCOLOR = BROWN

TILESIZE = 64
GRIDWIDTH = WIDTH / TILESIZE #32 wide
GRIDHEIGHT = HEIGHT /TILESIZE  #24 tall

WALL_IMG = 'tilegreen_39.png'

#player settings
PLAYER_HEALTH = 100
PLAYER_SPEED = 300 #300 pixels per second
PLAYER_ROT_SPEED = 250 #250 degrees per second
PLAYER_IMG = 'manBlue_gun.png'
#rectangle around player
PLAYER_HIT_RECT = pg.Rect(0,0,35,35)

#BARREL_OFFSET = vec(30,10)
#speed to push player backwards
KICKBACK = 200
#give the gun a little inaccruacy
GUN_SPREAD = 5

#Weapon settings
BULLET_IMG = 'bullet.png'
#WEAPON_IMG = 'shotgun.png'
WEAPON_OFFSET = vec(25,10)
WEAPON_IMG_RESIZE = .65 #65% of original picture size

WEAPONS = {}
#2d dictionary
WEAPONS['names'] = ['pistol','shotgun']

WEAPONS['pistol'] = {'bullet_speed':500,
                     'bullet_lifetime':1000, #disappears after 1000 milliseconds (1 second)
                     'rate': 250, #how many bullets shoot when you hold space down (how fast)
                     'kickback': 200,
                     'spread':5,
                     'damage':10, #10 points of damage
                     'bullet_size': 'lg',
                     'bullet_count': 1,
                     'barrel_offset': vec(30,10)}  #vector.how far from the center of the sprite, barrel of the gun is
                                                    #30 pixles x axis (right) and 10 pixles down (y axis)

WEAPONS['shotgun'] = {'bullet_speed': 400,
                      'bullet_lifetime': 500,
                      'rate': 900, #slower
                      'kickback': 300,
                      'spread':20,
                      'damage':5,
                      'bullet_size': 'sm',
                      'bullet_count': 12,
                      'image':'shotgun.png',
                      'barrel_offset': vec(75,10)}

WEAPONS['machine_gun'] = {'bullet_speed': 500,
                      'bullet_lifetime': 1000,
                      'rate': 50,
                      'kickback': 400,
                      'spread':10,
                      'damage':10,
                      'bullet_size': 'lg',
                      'bullet_count': 1,
                      'image':'machine_gun.png',
                      'barrel_offset': vec(75,10)}

WEAPONS['sniper'] = {'bullet_speed': 700,
                      'bullet_lifetime': 10000,
                      'rate': 900,
                      'kickback': 0,
                      'spread':0,
                      'damage':50,
                      'bullet_size': 'lg',
                      'bullet_count': 1,
                      'image':'sniper.png',
                      'barrel_offset': vec(68,10)}



#Mob settings
MOB_IMG = 'zombie1_hold.png'
MOB_SPEEDS = [150, 100, 75, 125]
MOB_HIT_RECT = pg.Rect(0,0,30,30)
MOB_HEALTH = 100
MOB_DAMAGE = 10
#distance that mob knocks back player
MOB_KNOCKBACK = 20
AVOID_RADIUS = 50 #pixels
DETECT_RADIUS = 400 #how far the zombies can see
#20 pixles forward and 20 pixles to the right
BLOOD_SPLAT_OFFSET = vec(30,0)

#Effects
MUZZLE_FLASES = ['whitePuff15.png','whitePuff16.png','whitePuff17.png','whitePuff18.png']
FLASH_DURATION = 40 #40milliseconds
BLOOD_SPLAT = ['bloodsplats_0001.png','bloodsplats_0002.png','bloodsplats_0003.png','bloodsplats_0004.png','bloodsplats_0005.png','bloodsplats_0006.png']
BLOOD_SPLAT_DURATION = 40 #40milliseconds
SPLAT = 'splat_green.png'
#this is a way to fade in an image in or out
DAMAGE_ALPHA = [i for i in range(0,255,25)]
NIGHT_COLOR = (20,20,20)
#how big your light shines
LIGHT_RADIUS = (500, 500)
SNIPER_LIGHT_RESIZE = 2.8 #2.8 times larger than original image

#drop the 4 for the orignal image
LIGHT_MASK = 'light_350_med.png'
SNIPER_LIGHT_MASK = 'light_350_med6.png'



#Layers
WALL_LAYER= 1
PLAYER_LAYER = 2
BULLET_LAYER =3
MOB_LAYER = 2
EFFECTS_LAYER = 4
ITEMS_LAYER=1

#Items
ITEM_IMAGES = {'health': 'health_pack.png',
               'shotgun': 'shotgun.png',
               'machine_gun': 'machine_gun.png',
               'sniper' : 'sniper.png'}

HEALTH_PACK_AMOUNT = 20
BOB_RANGE = 15 #pixels
BOB_SPEED = 0.4


# Sounds
BG_MUSIC = 'espionage.ogg'
PLAYER_HIT_SOUNDS = ['pain/8.wav', 'pain/9.wav', 'pain/10.wav', 'pain/11.wav']
ZOMBIE_MOAN_SOUNDS = ['brains2.wav', 'brains3.wav', 'zombie-roar-1.wav', 'zombie-roar-2.wav',
                      'zombie-roar-3.wav', 'zombie-roar-5.wav', 'zombie-roar-6.wav', 'zombie-roar-7.wav']
ZOMBIE_HIT_SOUNDS = ['splat-15.wav']

#for each type of weapon there will be a list of sounds
WEAPON_SOUNDS = {'pistol': ['pistol.wav'],
                 'shotgun':['shotgun.wav'],
                 'machine_gun': ['pistol.wav'],#change the machine gun sound later
                 'sniper': ['pistol.wav']} #change the machine gun sound later


EFFECTS_SOUNDS = {'level_start': 'level_start.wav',
                  'health_up': 'health_pack.wav',
                  'gun_pickup': 'gun_pickup.wav'}