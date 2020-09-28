#sprite classes

import pygame as pg
from random import uniform, choice, randint, random
from settings import *
from tilemap import collide_hit_rect
#can use these tweening/Easing animations for a lot of animations, e.g. pull up menu? (something to think about later)
import pytweening as tween
#vector to hold x,y coordinates
vec = pg.math.Vector2
from itertools import chain


def collide_with_walls(sprite, group, dir):
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            # if the walls center is greater than the players center, than player is on left side of wall
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                # put us on left hand side of wall we hit
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            # if the walls center is less than the players center, than player is on left side of wall
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                # put us on top of block
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            # sprite moving up
            if  hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y

class Player(pg.sprite.Sprite):
    #x and y GRID coordinates for player to spawn
    def __init__(self, game, x, y):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        #velocity vector
        self.vel = vec(0,0)
        #position vector
        self.pos = vec(x,y) #taking this out for tmx maps ...*TILESIZE
        #rotation
        self.rot = 0
        self.last_shot = 0
        self.health = PLAYER_HEALTH
        self.weapon = 'pistol'
        #self.weapon = 'shotgun'
        self.damaged = False

    def get_keys(self):
        self.rot_speed = 0
        self.vel = vec(0,0)
        keys=pg.key.get_pressed()
        #to disable diagnol movment, change all subsequent ifs to elifs
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.rot_speed = PLAYER_ROT_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rot_speed = -PLAYER_ROT_SPEED
        if keys[pg.K_UP] or keys[pg.K_w]:
            #move at the player speed in the x direction
            self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot)
        if keys[pg.K_DOWN] or keys[pg.K_a]:
            self.vel = vec(-PLAYER_SPEED / 2, 0).rotate(-self.rot)
        if keys[pg.K_SPACE]:
            self.shoot()

    def shoot(self):


        now = pg.time.get_ticks()
        if now -self.last_shot > WEAPONS[self.weapon]['rate']:
            self.last_shot = now
            #make a u"nit vector"
            dir = vec(1,0).rotate(-self.rot)
            #set bullets starting position at players position plus the offset for the specific gun rotated at the player's rotation
            pos = self.pos + WEAPONS[self.weapon]['barrel_offset'].rotate(-self.rot)
            # when we spawn the bullet, we'll change the players velocity by the kickback
            self.vel = vec(-WEAPONS[self.weapon]['kickback'], 0).rotate(-self.rot)
            for i in range(WEAPONS[self.weapon]['bullet_count']):
                spread = uniform(-WEAPONS[self.weapon]['spread'],WEAPONS[self.weapon]['spread'])
                Bullet(self.game, pos, dir.rotate(spread), WEAPONS[self.weapon]['damage'])
                #make a random choice for gun sound
                snd = choice(self.game.weapon_sounds[self.weapon])
                #if the sound is playing on more than 2 channels
                if snd.get_num_channels() >2:
                    #stop it
                    snd.stop()
                #play it new
                if not self.game.mute:
                    snd.play()
            MuzzleFlash(self.game,pos)

    def hit(self):
        self.damaged = True
        self.damage_alpha = chain(DAMAGE_ALPHA *2)

    def update(self):
        self.get_keys()
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        #rotate image

        #self.image = pg.transform.rotate(self.image, self.rot)
        self.image = pg.transform.rotate(self.game.player_img, self.rot)
        if self.damaged:
            #pulse red, alpha is how transparent a color is.
            # @ 9 minutes into part 21 he talks about a itertools.cycle
            #couldbe useful for animation
            try:
                #fill has special flags for effects
                self.image.fill((255,0,0, next(self.damage_alpha)),special_flags = pg.BLEND_RGBA_MULT)
            except:
                self.damaged = False
        #calculate new sprite rectangle to keep rotation smooth
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        #game.dt adjusts for lag
        self.pos +=self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls,'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls,'y')
        self.rect.center = self.hit_rect.center

    def add_health(self, amount):
        self.health += amount
        if self.health > PLAYER_HEALTH:
            self.health = PLAYER_HEALTH

class Weapon(pg.sprite.Sprite):
    def __init__(self, game, playerPos):
        self._layer = BULLET_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.weapon_img
        self.rect = self.image.get_rect()
        self.rect.center = playerPos
        #self.image = pg.transform.rotate(self.image, 90)
        self.pos = playerPos + WEAPON_OFFSET
        self.rect.center = self.pos

    def update(self):
        if self.game.player.weapon == 'pistol':
            self.kill()
        self.image = pg.transform.rotate(self.game.weapon_img, self.game.player.rot)
        self.rect = self.image.get_rect()
        self.pos = vec(int(self.game.player.pos.x), int(self.game.player.pos.y)) + WEAPON_OFFSET.rotate(-self.game.player.rot)
        self.rect.center = self.pos

class Mob(pg.sprite.Sprite):
    #spawn location based on tile grid
    def __init__(self, game, x, y):
        self._layer = MOB_LAYER
        #make mobs part of all sprites group and part of the mobs group
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mob_img.copy()
        self.rect = self.image.get_rect()
        self.rect.center=(x,y)
        self.hit_rect = MOB_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.pos = vec(x,y)# remove this for Tiled maps.. *TILESIZE
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.rect.center = self.pos
        self.rot = 0
        self.health = MOB_HEALTH
        self.speed = choice(MOB_SPEEDS)
        self.target = game.player

    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob!= self:
                dist = self.pos - mob.pos
                if 0 <dist.length() < AVOID_RADIUS:
                    #determines angle, normalize sets distance to 1
                    self.acc +=dist.normalize()


    def update(self):
        target_dist = self.target.pos - self.pos
        #checks if the zombie can "see you"
        #length of the vector
        if target_dist.length_squared() < DETECT_RADIUS**2:
            #zombie randomly makes sound when they are chasing the player
            #the lower the number the less frequent
            if random()<0.002:
                if not self.game.mute:
                    choice(self.game.zombie_moan_sounds).play()
            #when the mob updates, it needs to see where the player is
            #and figure out what angle to rotate to, to point at the player

            #this is a geometery fancy way of calculating rotaton needed
            self.rot = target_dist.angle_to(vec(1,0))
            #rotate image by self.rot angle
            self.image = pg.transform.rotate(self.game.mob_img, self.rot)
            self.rect = self.image.get_rect()
            self.rect.center = self.pos
            #declutter zombies, avoid each other
            #start with unit vector
            self.acc = vec(1,0).rotate(-self.rot)
            #method to avoid other mobs
            self.avoid_mobs()
            self.acc.scale_to_length(self.speed)
            self.acc +=self.vel * -1
            self.vel += self.acc * self.game.dt
            self.pos += self.vel * self.game.dt + 0.5 *self.acc *self.game.dt **2
            self.hit_rect.centerx = self.pos.x
            collide_with_walls(self, self.game.walls, 'x')
            self.hit_rect.centery = self.pos.y
            collide_with_walls(self, self.game.walls, 'y')
            self.rect.center = self.hit_rect.center
        if self.health <=0:
            if not self.game.mute:
                choice(self.game.zombie_hit_sounds).play()
            self.kill()
            #draw splat where zombie was minus half of zombie size to center it
            self.game.map_img.blit(self.game.splat, self.pos - vec(32,32))


    def draw_health(self):
        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col= YELLOW
        else:
            col = RED
        #width of the health bar will be a percent of the width of the mob
        width = int(self.rect.width*self.health/MOB_HEALTH)
        self.health_bar = pg.Rect(0,0, width, 7)
        if self.health <MOB_HEALTH:
            pg.draw.rect(self.image, col, self.health_bar)

class Bullet(pg.sprite.Sprite):
    #position to spawn
    #direction to travel
    def __init__(self, game, pos, dir, damage):
        self._layer = BULLET_LAYER
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.bullet_images[WEAPONS[game.player.weapon]['bullet_size']]
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = vec(pos)
        self.rect.center = pos
        if game.player.weapon == 'sniper':
            self.vel = dir * WEAPONS[game.player.weapon]['bullet_speed'] #no change in velocity for sniper in order to improve red dot accuracy
        else:
            self.vel = dir * WEAPONS[game.player.weapon]['bullet_speed'] * uniform(0.9,1.1) #create some change in velocity
        #track spawn time
        self.spawn_time = pg.time.get_ticks()
        self.damage = damage

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self, self.game.walls):
            # delete bullet
            self.kill()
            print('Bullet collided w/ wall at x: ',self.rect.x, ' and y: ',self.rect.y)
        if pg.time.get_ticks() - self.spawn_time > WEAPONS[self.game.player.weapon]['bullet_lifetime']:
            #delete bullet
            self.kill()

class RedDot(pg.sprite.Sprite):
    #position to spawn
    #direction to travel
    def __init__(self, game, pos, dir):
        #self._layer = BULLET_LAYER
        #self.groups = game.all_sprites, game.bullets
        #pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.bullet_images[WEAPONS[game.player.weapon]['bullet_size']]
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = vec(pos)
        self.rect.center = pos
        self.vel = dir * WEAPONS[game.player.weapon]['bullet_speed']
        #track spawn time
        self.spawn_time = pg.time.get_ticks()

    def findEnd(self):
        #move invisible bullet until it collides with wall
        while not pg.sprite.spritecollideany(self, self.game.walls):
            self.pos += self.vel * self.game.dt
            self.rect.center = self.pos

        return self.rect.x, self.rect.y




#this is a wall for text maps
class Wall(pg.sprite.Sprite):
    #spawn location based on tile grid
    def __init__(self, game, x, y):
        self._layer = WALL_LAYER
        #make wall part of all sprites group and part of the walls group
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)

        self.game = game
        #create a surface
        self.image = game.wall_img
        #get the rectangle area of the surface
        self.rect = self.image.get_rect()
        self.x = x
        self.y =y
        self.rect.x = x *TILESIZE
        self.rect.y = y * TILESIZE

#invisble object on top of wall (this is useful for the object layer from Tiled
class Obstacle(pg.sprite.Sprite):
    # spawn location based on tile grid
    def __init__(self, game, x, y, w, h):
        self._layer = WALL_LAYER
        # make wall part of all sprites group and part of the walls group
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # create a surface
        # get the rectangle area of the surface
        self.rect = pg.Rect(x,y,w,h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

class MuzzleFlash(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self._layer = EFFECTS_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        size = randint(20,50)
        self.image = pg.transform.scale(choice(game.gun_flashes), (size, size))
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.center = pos
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        if pg.time.get_ticks() - self.spawn_time > FLASH_DURATION:
            self.kill()

#my attempt
class BloodSplat(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self._layer = EFFECTS_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        size = randint(20,50)
        self.image = pg.transform.scale(choice(game.blood_splat), (size, size))
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.center = pos
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        if pg.time.get_ticks() - self.spawn_time > BLOOD_SPLAT_DURATION:
            self.kill()

class Item(pg.sprite.Sprite):
    def __init__(self, game, pos, type):
        self._layer = ITEMS_LAYER
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.item_image[type]
        self.rect = self.image.get_rect()
        self.type = type
        self.pos = pos
        self.rect.center = pos
        #animations
        #input 0 to 1 and it returns 0 to 1 based on y axis animaton
        self.tween = tween.easeInOutSine
        self.step = 0
        self.dir = 1

    #item bobbing animation
    def update(self):
        #bobbing motion
        #calculate how far you are in the range as a % of BOB Range
        offset = BOB_RANGE * (self.tween(self.step/BOB_RANGE) -0.5)
        self.rect.centery = self.pos.y + offset *self.dir
        self.step += BOB_SPEED
        if self.step > BOB_RANGE:
            self.step = 0
            self.dir *=-1