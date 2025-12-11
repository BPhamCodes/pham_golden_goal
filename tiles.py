# tiles.py - Contains Spritesheet, Tile, and TileMap classes
import pygame as pg
import csv
import os
from io import StringIO 

# --- CONFIGURATION CONSTANTS (Must match your settings.py and main.py) ---
TILE_SIZE = 32
SPRITESHEET_UNIT = 16 

# Maps tile index (string) to the top-left pixel coordinate (of the 16x16 unit)
# where the 32x32 tile starts on the spritesheet.
TILE_COORDS_32 = {
    '1': (SPRITESHEET_UNIT * 4, SPRITESHEET_UNIT * 6),
    '2': (SPRITESHEET_UNIT * 5, SPRITESHEET_UNIT * 6),
    '6': (SPRITESHEET_UNIT * 0, SPRITESHEET_UNIT * 1),
    '33': (SPRITESHEET_UNIT * 0, SPRITESHEET_UNIT * 2),
    '5': (SPRITESHEET_UNIT * 0, SPRITESHEET_UNIT * 0),
    '39': (SPRITESHEET_UNIT * 0, SPRITESHEET_UNIT * 8),
    '40': (SPRITESHEET_UNIT * 0, SPRITESHEET_UNIT * 9),
    '11': (SPRITESHEET_UNIT * 1, SPRITESHEET_UNIT * 0),
    '20': (SPRITESHEET_UNIT * 1, SPRITESHEET_UNIT * 1),
    '26': (SPRITESHEET_UNIT * 0, SPRITESHEET_UNIT * 3),
    '31': (SPRITESHEET_UNIT * 1, SPRITESHEET_UNIT * 9),
    '0': (SPRITESHEET_UNIT * 1, SPRITESHEET_UNIT * 6),
    '17': (SPRITESHEET_UNIT * 4, SPRITESHEET_UNIT * 4),
    '27': (SPRITESHEET_UNIT * 5, SPRITESHEET_UNIT * 4),
    '28': (SPRITESHEET_UNIT * 0, SPRITESHEET_UNIT * 7),
    '8': (SPRITESHEET_UNIT * 0, SPRITESHEET_UNIT * 6),
    '4': (SPRITESHEET_UNIT * 8, SPRITESHEET_UNIT * 4),
    '15': (SPRITESHEET_UNIT * 0, SPRITESHEET_UNIT * 4),
    '22': (SPRITESHEET_UNIT * 6, SPRITESHEET_UNIT * 7),
    '23': (SPRITESHEET_UNIT * 7, SPRITESHEET_UNIT * 7),
    '36': (SPRITESHEET_UNIT * 0, SPRITESHEET_UNIT * 5),
    '37': (SPRITESHEET_UNIT * 1, SPRITESHEET_UNIT * 5),
    '7': (SPRITESHEET_UNIT * 6, SPRITESHEET_UNIT * 6),
    '18': (SPRITESHEET_UNIT * 5, SPRITESHEET_UNIT * 7),
    '21': (SPRITESHEET_UNIT * 2, SPRITESHEET_UNIT * 6),
    '-1': None
}

class Spritesheet():
    """Handles loading the spritesheet and parsing individual tiles."""
    def __init__(self, filename):
        try:
            # Note: filename here should be the full path passed from Game.load_data()
            self.sheet = pg.image.load(filename).convert_alpha()
        except pg.error as e:
            print(f"Error: Unable to load spritesheet image: {filename}")
            raise SystemExit(e)

    def get_image_at(self, rect):
        """Loads a region from the spritesheet using a Pygame Rect."""
        image = pg.Surface(rect.size, pg.SRCALPHA)
        image.blit(self.sheet, (0, 0), rect)
        return image

    def parse_sprite_32(self, tile_index_str):
        """Pulls a 32x32 region from the spritesheet for the game tile."""
        if tile_index_str not in TILE_COORDS_32 or TILE_COORDS_32[tile_index_str] is None:
            return pg.Surface((TILE_SIZE, TILE_SIZE), pg.SRCALPHA)
            
        x, y = TILE_COORDS_32[tile_index_str]
        rect = pg.Rect(x, y, TILE_SIZE, TILE_SIZE) 
        
        return self.get_image_at(rect)


class Tile(pg.sprite.Sprite):
    """Represents a single tile in the game world."""
    def __init__(self, image: pg.Surface, x: int, y: int):
        pg.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def draw(self, surface: pg.Surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))

class TileMap():
    """Manages the map structure, loading, and rendering."""
    
    # Hardcoded map data fallback (usually stored in main or a separate map file)
    MAP_DATA_STRING = """

"33","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","33""""""
33","5","15","36","37","37","37","37","37","37","37","37","37","37","37","37","37","37","37","37","37","37","37","37","37","37","37","37","37","38","20","33"""""""
33","6","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","5","33"""""""
33","6","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","11","33"""""""
39","39","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","17","27","27","-1","-1","-1","-1","-1","11","33"""""""
6","6","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","17","27","7","7","7","7","7","1","21","20","33"""""""
26","6","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","0","0","0","0","0","0","0","8","8","8","8","8","8","8","20","33"""""""
33","15","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","8","8","8","8","8","8","39","39","39","39","39","39","39","39","20","33"""""""
33","6","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","17","17","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","20","33"""""""
40","31","-1","-1","-1","-1","-1","-1","-1","-1","-1","17","17","27","27","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","20","33"""""""
6","6","1","2","1","0","0","-1","P","-1","17","27","27","27","27","17","-1","-1","-1","-1","-1","-1","-1","-1","-1",-1","-1","-1","-1","-1","5","33"""""""
6","6","10","10","10","10","10","10","10","8","8","8","8","8","8","16","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","20","33"""""""
6","6","28","28","28","28","28","28","28","15","28","28","4","28","28","28","28","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","20","33"""""""
6","6","28","28","28","28","15","28","28","28","28","23","22","23","28","28","28","6","6","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","11","33"""""""
6","5","39","39","39","39","39","39","39","39","39","39","39","39","39","39","39","39","39","-1","-1","-1","-1","-1","-1","-1","-1","-1","17","-1","11","33"""""""
6","6","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","17","27","27","17","11","33"""""""
6","20","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","17","27","27","27","27","11","26
6","6","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","18","1","21","21","18","18","1","2","18","18","33"""""""
6","6","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","18","9","9","9","9","9","9","9","9","9","9","33""""""
6","11","-1","17","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","6","6","20","4","20","20","20","20","20","35","20","20","33""""""
6","11","17","27","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","6","6","20","20","23","24","24","23","6","6","6","6","35","33""""""
6","11","27","27","17","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","-1","25","33""""""
20","6","36","37","37","37","37","37","37","37","37","37","37","37","37","37","37","37","37","37","37","37","37","37","37","37","37","37","37","38","28","40
6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6","6"
    """

    def __init__(self, spritesheet: Spritesheet, raw_map_data):
        self.tile_size = TILE_SIZE 
        self.start_x, self.start_y = 0, 0
        self.spritesheet = spritesheet
        self.raw_map_data = raw_map_data
        self.tiles = self._load_tiles()
        
        self.map_w = len(self.raw_map_data[0]) * TILE_SIZE
        self.map_h = len(self.raw_map_data) * TILE_SIZE

        self.map_surface = pg.Surface((self.map_w, self.map_h))
        self.map_surface.set_colorkey((0, 0, 0))
        self._load_map_surface()

    def draw_map(self, surface: pg.Surface):
        surface.blit(self.map_surface, (0, 0))

    def _load_map_surface(self):
        for tile in self.tiles:
            tile.draw(self.map_surface)

    def _load_tiles(self):
        tiles = []
        y = 0
        
        for row in self.raw_map_data:
            x = 0
            for tile_index in row:
                tile_index = tile_index.strip()
                
                if tile_index in TILE_COORDS_32 and TILE_COORDS_32[tile_index] is not None:
                    
                    image = self.spritesheet.parse_sprite_32(tile_index)
                    
                    if tile_index == '0':
                        self.start_x, self.start_y = x * self.tile_size, y * self.tile_size
                        tiles.append(Tile(image, x * self.tile_size, y * self.tile_size))
                    
                    else:
                         tiles.append(Tile(image, x * self.tile_size, y * self.tile_size))
                
                x += 1
            y += 1
        return tiles