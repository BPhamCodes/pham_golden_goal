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
      self.map_state = 1
      self.transitioning = False
      self.red_flash = False
      self.red_flash_start = 0
      self.red_flash_duration = 500
      self.red_flash_timer = 0
      self.red_flash_interval = 1200

      self.level3_start_time = 0
      self.level3_duration = 30
      self.time = self.level3_duration


      # self.darkness enables transparceny with pg.SCRALPHA
      self.darkness = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
      self.vision_radius = 120  # change size of visible circle

   # sets up a game folder directory path using the current folder containing THIS file
   # give the Game class a map property which uses the Map class to parse the level1.txt file
   # loads image files from images folder
   def load_data(self):
      self.game_folder = path.dirname(__file__)
      self.img_folder = path.join(self.game_folder, 'images')

      # Choose map file based on map_state
      if self.map_state == 3:
         map_file = 'level3.txt'
         self.show_level_intro("LEVEL 3   FINAL   STRETCH", YELLOW)
         self.level3_start_time = pg.time.get_ticks()
         self.time = self.level3_duration

      if self.map_state == 2:
         map_file = 'level2.txt'
         self.show_level_intro("LEVEL 2   STORAGE   ROOM", YELLOW)
      if self.map_state == 1:
         map_file = 'level1.txt'
         self.show_level_intro("LEVEL 1   HALLWAY", YELLOW)


      self.map = Map(path.join(self.game_folder, map_file))
      self.tile_img = pg.image.load(path.join(self.img_folder, 'tiles.png')).convert_alpha()


   # Defines new data and sprite groups
   # inputs the sprites based off the tilemap
   def new(self):
    # the sprite Group allows us to upate anwd draw sprite in grouped batches
    self.load_data()
    self.transitioning = False
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
    self.playing = True

    # places the sprite based off the tilemap
    #self.sword = Sword(self, 0,0)
    for row, tiles in enumerate(self.map.data):
        for col, tile in enumerate(tiles):
            if tile == '1':
                Wall(self, col, row, "unmoveable")
            elif tile == '2':
                Wall(self, col, row, "moveable")
            elif tile == '3':
                Vent(self, col, row)
            elif tile == "4":
                Box(self, col, row, drops_key = False)
            elif tile == "5":
                Box(self, col, row, drops_key = True)
            elif tile == "6":
                Spotlight(self, col, row)
            elif tile == "D":
                Door(self, col, row)
            elif tile == "L":
                Lastdoor(self, col, row)
            

            elif tile == 'S':
                Screwdriver(self, col, row)
            elif tile == 'C':
                Crowbar(self, col, row)
            elif tile == 'P':
                self.player = Player(self, col, row)
            elif tile == 'M':
                Mob(self, col, row)
            

            self.floor_tiles.append((col, row))
    
   # Runs the program and calls the function
   def run(self):
      while self.playing:
         self.dt = self.clock.tick(FPS) / 1000
         # input
         self.events()
         # process
         self.update() 
         # output
         self.draw()
   
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
      if self.map_state == 3:
         now = pg.time.get_ticks()
         # trigger flash every interval
         if now - self.red_flash_timer > self.red_flash_interval:
            self.red_flash = True
            self.red_flash_start = now
            self.red_flash_timer = now
         elapsed = (pg.time.get_ticks() - self.level3_start_time) // 1000
         self.time = max(0, self.level3_duration - elapsed)

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
      self.darkness.fill((0, 0, 0, 235))
      px, py = self.player.rect.center
      # Circle around player's x and y
      pg.draw.circle(self.darkness, (0, 0, 0, 0), (int(px), int(py)), self.vision_radius)
      self.screen.blit(self.darkness, (0, 0))

   # Draws the elements on the screen
   def draw(self):
      self.screen.fill(GREY)
      # tiles
      for col, row in self.floor_tiles:
         self.screen.blit(self.tile_img, (col * TILESIZE[0], row * TILESIZE[1]))
      self.all_sprites.draw(self.screen)

      if self.red_flash:
         now = pg.time.get_ticks()
         if now - self.red_flash_start <= self.red_flash_duration:
            overlay = pg.Surface(self.screen.get_size())
            overlay.fill((255, 0, 0))
            overlay.set_alpha(40)
            self.screen.blit(overlay, (0, 0))
         else:
            self.red_flash = False

      # draw mob vision triangles on top of sprites
      for mob in self.all_mobs:
         mob.draw_vision(self.screen)
      self.draw_darkness()
      self.draw_text(self.screen, str(self.player.health), 30, WHITE, 282, 45)
      if self.map_state == 1: 
         self.draw_text(self.screen, "FIND    A     TOOL    TO    USE", 15, YELLOW, WIDTH-200, 50)
      if self.map_state == 2:
         self.draw_text(self.screen, "FIND    A     TOOL    TO    OPEN   THE    BOXES", 15, YELLOW, WIDTH-200, 50)
      if self.map_state == 3:
         self.draw_text(self.screen, f"ALL     DOORS     WILL     LOCK     IN    {self.time}    SECONDS", 40, WHITE, 337, 100)
      self.player.draw_health_bar(self.screen)
      self.player.draw_inventory(self.screen)


      pg.display.flip()

   def show_level_intro(self, text, color):
      self.screen.fill(BLACK)
      self.draw_text(self.screen, text, 48, color, WIDTH / 2, HEIGHT / 4)
      pg.display.flip()

      # Lock input for 2 seconds
      lockout_start = pg.time.get_ticks()
      while pg.time.get_ticks() - lockout_start < 2000:
         # Still process QUIT events so window doesn't freeze
         for event in pg.event.get():
               if event.type == pg.QUIT:
                  self.running = False
                  return

      # After 2 seconds, allow any key to continue
      self.wait_for_key()

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
    g = Game()
    g.show_start_screen()
    while g.running:
        g.new()
        g.run()
    pg.quit()
