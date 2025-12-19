# Created by Brendon Pham
# import necessary modules
# core game loop
# input
# update
# draw

# imports the modules from the library such as math, random, sys, and pygame
# imports other methods from other files
# Start screen from Mr. Cozart

# yay I can use github from vs CODE
# Uncomment screen.bg_img and self.screen.blit(self.bg_img, (0, 0))
import math
import random
import sys
import pygame as pg
from settings import *
from sprites import *
from os import path
from utils import *
from math import floor

# Class to run the entire program
class Game:
   def __init__(self):
      pg.init()
      self.clock = pg.time.Clock()
      self.screen = pg.display.set_mode((WIDTH, HEIGHT))
      pg.display.set_caption("Shadow Escape!")
      self.playing = True
      self.running = True

      # self.darkness enables transparceny with pg.SCRALPHA
      self.darkness = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
      self.vision_radius = 120  # change size of visible circle

   # sets up a game folder directory path using the current folder containing THIS file
   # give the Game class a map property which uses the Map class to parse the level1.txt file
   # loads image files from images folder
   def load_data(self):
      self.game_folder = path.dirname(__file__)
      self.img_folder = path.join(self.game_folder, 'images')
      self.map = Map(path.join(self.game_folder, 'level1.txt'))
      # loads image into memory when a new game is created and load_data is called
      self.tile_img = pg.image.load(path.join(self.img_folder, 'tiles.png')).convert_alpha()
     # self.bg_img = pg.image.load(path.join(self.img_folder, 'grass_bg.png')).convert_alpha()
     # self.bg_img = pg.transform.scale(self.bg_img, (WIDTH, HEIGHT))

   # Defines new data and sprite groups
   # inputs the sprites based off the tilemap
   def new(self):
    # the sprite Group allows us to upate anwd draw sprite in grouped batches
    self.load_data()
    # create all sprite groups
    self.all_sprites = pg.sprite.Group()
    self.all_mobs = pg.sprite.Group()
    self.all_items = pg.sprite.Group()
    self.all_walls = pg.sprite.Group()
    self.all_projectiles = pg.sprite.Group()
    self.all_swords = pg.sprite.Group() 
    self.all_moveable_balls = pg.sprite.Group()
    self.all_searchables = pg.sprite.Group()
    self.floor_tiles = []

    # places the sprite based off the tilemap
    #self.sword = Sword(self, 0,0)
    for row, tiles, in enumerate(self.map.data):
        # print(row)
        for col, tile, in enumerate(tiles):
            # print(col)
            if tile == '1':
                Wall(self, col, row, "unmoveable")
            if tile == '2':
                Wall(self, col, row, "moveable")
            if tile == '3':
                Vent(self, col, row)
            if tile == '.':
                pass
            elif tile == 'S':
                Screwdriver(self, col, row)
            elif tile == 'P':
                self.player = Player(self, col, row)
            elif tile == 'M':
                Mob(self, col, row)
            # tiles for the background
            self.floor_tiles.append((col, row))

   # Runs the program and calls the function
   def run(self):
      while self.playing == True:
         self.dt = self.clock.tick(FPS) / 1000
         # input
         self.events()
         # process
         self.update()
         # output
         self.draw()
      pg.quit()
   # Checks for any events that occur in the game based off of the input
   def events(self):
      for event in pg.event.get():
         if event.type == pg.QUIT:
            if self.playing:
               self.playing = False
            self.running = False

         # Checks for inputs on left control and sets crouching state to true or false
         # Calls crouch function in Player class
         if event.type == pg.KEYDOWN:
            if event.key == pg.K_LCTRL:
               self.vision_radius = 70
               self.player.crouching = True
               self.player.crouch()
         # If the player stops holding left control
         if event.type == pg.KEYUP:
            if event.key == pg.K_LCTRL:
               self.vision_radius = 120
               self.player.try_uncrouch()
   # updates the game's sprites, time, screwdrivers
   def update(self):
      self.all_sprites.update()
      seconds = pg.time.get_ticks()//1000 
      countdown = 10
      self.time = countdown - seconds

   # Provides the basic settings to draw text
   def draw_text(self, surface, text, size, color, x, y):
        #font_name = pg.font.match_font('lower-pixel-regular')
        font_name = pg.font.match_font('ArcadeClassic')
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x,y)
        surface.blit(text_surface, text_rect)
   # Draw darkness over the whole screen
   def draw_darkness(self):
      self.darkness.fill((0, 0, 0, 245))

      px, py = self.player.rect.center

      # Circle around player's x and y
      pg.draw.circle(self.darkness, (0, 0, 0, 0), (int(px), int(py)), self.vision_radius)

      self.screen.blit(self.darkness, (0, 0))

   # Draws the elements on the screen
   def draw(self):
      self.screen.fill(GREY)

      # draw floor tiles
      for col, row in self.floor_tiles:
         self.screen.blit(self.tile_img,(col * TILESIZE[0], row * TILESIZE[1]))
 
      self.all_sprites.draw(self.screen)
      # draw mob vision triangles on top of sprites
      for mob in self.all_mobs:
         mob.draw_vision(self.screen)

      self.draw_darkness()
      self.draw_text(self.screen, str(self.player.health), 30, WHITE, 282, 45)
      #self.draw_text(self.screen, str(self.player.coins), 24, WHITE, 400, 100)
      #self.draw_text(self.screen, str(self.time), 24, WHITE, 500, 100)
      self.player.draw_health_bar(self.screen)
      self.player.draw_inventory(self.screen)

      pg.display.flip()


   def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:
                    waiting = False
   def show_start_screen(self):
        # game splash/start screen
      #   pg.mixer.music.load(path.join(self.snd_dir, 'Yippee.ogg'))
      #   pg.mixer.music.play(loops=-1)
        self.screen.fill(BLACK)
        self.draw_text(self.screen,"ALWAYS   STAY   OUT   OF   LIGHT", 48, WHITE, WIDTH / 2, HEIGHT / 4)
        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.fadeout(500)

if __name__ == "__main__":
#    creating an instance or instantiating the Game class
   g = Game()
   g.show_start_screen()
   while g.running:
      g.new()
      g.run()