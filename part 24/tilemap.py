import pygame as pg
from settings import *
import pytmx

#takes two sprites
def collide_hit_rect(one, two):
    #compare players hit rect with wall inside of normal rect
    return one.hit_rect.colliderect(two.rect)

class Map:
    def __init__(self, filename):
        #store each line of text file
        self.data = []
        with open(filename,'rt') as f:
            for line in f:
                #reach each line and strip away hidden /n characters
                self.data.append(line.strip())

        #wide of the map is the length of one of the lines from the mapdata
        self.tilewidth = len(self.data[0])
        #map height is the number of lines in the map file
        self.tileheight = len(self.data)
        #how many pixels in map
        self.width = self.tilewidth *TILESIZE
        self.height = self.tileheight*TILESIZE

class TiledMap:
    def __init__(self, filename):
        tm = pytmx.load_pygame(filename, pixelalpha = True)
        #50 tiles x 64 pixels each
        self.width = tm.width *tm.tilewidth
        self.height = tm.height *tm.tileheight
        self.tmxdata = tm

    def render(self,surface):
        #alias tile image command
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            #if layer is a tile layer (vs object and image)
            if isinstance(layer,pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile =ti(gid)
                    if tile:
                        surface.blit(tile,(x*self.tmxdata.tilewidth, \
                                           y*self.tmxdata.tileheight))
    def make_map(self):
        #create surface
        temp_surface = pg.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface

class Camera:
    #accepts width and height in number of pixels on map
    def __init__(self, width, height):

        #sets up the camera rectangle based on size of the map
        self.camera = pg.Rect(0,0,width,height)
        self.width = width
        self.height = height

    #returns the rectangle for any sprite we want to follow
    def apply(self, entity):
        #this moves the sprite by how much the camera moved
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    #updte camera to track where the player is
    #the camera will draw the entire map, but will ofset the map based on
    #where the plauer is
    def update(self,target):
        # calculate offset in opposite direction of player movement,
        # and keep the player in the center of the screen
        x = -target.rect.centerx + int(WIDTH/2)
        y = -target.rect.centery + int(HEIGHT/2)

        #limit scrollng to map size
        x = min(0,x) #lef
        y= min(0, y) #top

        x = max(-(self.width - WIDTH), x) #right
        y = max(-(self.height-HEIGHT), y) #bottom

        #move the camera's rectangle
        self.camera = pg.Rect(x, y, self.width, self.height)



