# File created by: Brendon Pham

# The sprites module contains all the sprites
# Sprites include: player, mob - moving object

# Imports methods from the pygame library
# Imports methods from other files
import pygame as pg
from pygame.sprite import Sprite
from settings import *
from utils import Cooldown
from utils import Spritesheet
from random import randint
from random import choice
from os import path
vec = pg.math.Vector2

# https://www.youtube.com/watch?v=ST-Qq3WBZBE: source to add jump
# Used help from ChatGPT with jumping

# Class under parent class Sprite
# Defines a new sprite that the player can control based off key inputs
# Collisions will be detected (walls, coins, and ball(s))
class Player(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game

        # Player's sprite's images
        self.spritesheet_idle = Spritesheet(path.join(self.game.img_folder, "spritesheet_idle.png"))
        self.spritesheet_walk_right = Spritesheet(path.join(self.game.img_folder, "spritesheet_anim_walking_right.png"))
        self.spritesheet_walk_left = Spritesheet(path.join(self.game.img_folder, "spritesheet_anim_walking_left.png"))
        self.spritesheet_jump_right = Spritesheet(path.join(self.game.img_folder, "spritesheet_anim_jumping_right.png"))
        self.spritesheet_jump_left = Spritesheet(path.join(self.game.img_folder, "spritesheet_anim_jumping_left.png"))
        
        self.spritesheet_crouch_idle = Spritesheet(path.join(self.game.img_folder, "spritesheet_anim_crouching_idle.png"))
        self.spritesheet_crouch_right = Spritesheet(path.join(self.game.img_folder, "spritesheet_anim_crouching_walk_right.png"))
        self.spritesheet_crouch_left = Spritesheet(path.join(self.game.img_folder, "spritesheet_anim_crouching_walk_left.png"))

        self.load_images()
        self.image = pg.Surface((32, 32))
        self.rect = self.image.get_rect()
        self.vel = vec(0,0)
        self.pos = vec(x,y) * TILESIZE[0]
        self.speed = 150
        self.health = 100
        self.coins = 0
        self.cd = Cooldown(1000)
        self.weapon_cd = Cooldown(1000)
        self.dir = vec(0,0)

        # Variables used for boolean expressions
        self.walking = False
        self.jumping = False
        self.running_right = False
        self.running_left = False
        self.attacking = False
        self.jumping = False
        self.crouching = False
        self.searching = False
        
        self.current_frame = 0
        self.last_update = 0

        self.jump_height = 15
        self.y_velocity = self.jump_height

    # loads images for the idle and running frames
    def load_images(self):
        # Loops throughout the idle animation png and appends a frame into a list
        # Calls list to get each image
        self.standing_frames = [
            self.spritesheet_idle.get_image(0, 0, 64, 64),
            self.spritesheet_idle.get_image(0, 64, 64, 64)]
        for frame in self.standing_frames:
            frame.set_colorkey(BLACK)

        # Loops throughout the running animation png and appends a frame into a list
        # Calls list to get each image
        self.running_frames_right = []
        for i in range(11):
            frame = self.spritesheet_walk_right.get_image(0, i * 64, 64, 64)
            frame.set_colorkey(BLACK)
            self.running_frames_right.append(frame)
        
        # Loops throughout the running animation png and appends a frame into a list
        # Calls list to get each image
        self.running_frames_left = []
        for i in range(11):
            frame = self.spritesheet_walk_left.get_image(0, i * 64, 64, 64)
            frame.set_colorkey(BLACK)
            self.running_frames_left.append(frame)

        # Loops throughout the running animation png and appends a frame into a list
        # Calls list to get each image
        self.jumping_frames_right = []
        for i in range(6):
            frame = self.spritesheet_jump_right.get_image(0, i * 64, 64, 64)
            frame.set_colorkey(BLACK)
            self.jumping_frames_right.append(frame)

        # Loops throughout the running animation png and appends a frame into a list
        # Calls list to get each image
        self.jumping_frames_left = []
        for i in range(6):
            frame = self.spritesheet_jump_left.get_image(0, i * 64, 64, 64)
            frame.set_colorkey(BLACK)
            self.jumping_frames_left.append(frame)
        
        # Loops throughout the running animation png and appends a frame into a list
        # Calls list to get each image
        self.crouching_frames_idle = []
        for i in range(2):
            frame = self.spritesheet_crouch_idle.get_image(0, i * 64, 64, 64)
            frame.set_colorkey(BLACK)
            self.crouching_frames_idle.append(frame)

        # Loops throughout the running animation png and appends a frame into a list
        # Calls list to get each image
        self.crouching_frames_right = []
        for i in range(4):
            frame = self.spritesheet_crouch_right.get_image(0, i * 64, 64, 64)
            frame.set_colorkey(BLACK)
            self.crouching_frames_right.append(frame)
        
        # Loops throughout the running animation png and appends a frame into a list
        # Calls list to get each image
        self.crouching_frames_left = []
        for i in range(4):
            frame = self.spritesheet_crouch_left.get_image(0, i * 64, 64, 64)
            frame.set_colorkey(BLACK)
            self.crouching_frames_left.append(frame)

    # Creates the animations for the idle and running
    def animate(self):
        now = pg.time.get_ticks()
        # creates the running animation if the player is crouching and idle
        # With time per frame
        if self.crouching and not self.running_right and not self.running_left:
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.crouching_frames_idle)
                bottom = self.rect.bottom
                self.image = self.crouching_frames_idle[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        # creates the running animation if the player is idle
        if not self.jumping and not self.walking:
            if now - self.last_update > 350:
                # print(now)
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        # creates the running animation if the player is moving right
        # With time per frame
        if self.running_right and not self.jumping and not self.crouching:
            if now - self.last_update > 50:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.running_frames_right)
                bottom = self.rect.bottom
                self.image = self.running_frames_right[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        # creates the running animation if the player is moving left
        # With time per frame
        if self.running_left and not self.jumping and not self.crouching:
            if now - self.last_update > 50:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.running_frames_left)
                bottom = self.rect.bottom
                self.image = self.running_frames_left[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        # creates the jumping animation if the player is moving left and is jumping
        # With time per frame
        if self.jumping and self.running_left:
            if now - self.last_update > 200:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.jumping_frames_left)
                bottom = self.rect.bottom
                self.image = self.jumping_frames_left[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        # creates the running animation if the player is moving right and jumping, or is just jumping
        # With time per frame
        if (self.jumping and self.running_right) or self.jumping:
            if now - self.last_update > 200:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.jumping_frames_right)
                bottom = self.rect.bottom
                self.image = self.jumping_frames_right[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        # creates the running animation if the player is crouching and walking right
        # With time per frame
        if self.crouching and self.running_right:
            if now - self.last_update > 200:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.crouching_frames_right)
                bottom = self.rect.bottom
                self.image = self.crouching_frames_right[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        # creates the running animation if the player is crouching and walking left
        # With time per frame
        if self.crouching and self.running_left:
            if now - self.last_update > 200:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.crouching_frames_left)
                bottom = self.rect.bottom
                self.image = self.crouching_frames_left[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        
        
    # def attack(self):
    #     if not self.attacking and self.weapon_cd.ready():
    #         self.weapon_cd.start()
    #         self.attacking = True
    #         print ("attacking")
    #         self.weapon = Sword(self.game, self.rect.x, self.rect.y)
    
    # Identifies the keys the user inputs and moves the player accordingly
    def get_keys(self):
        self.vel = vec(0,0)
        keys = pg.key.get_pressed()
        self.running_right = False
        self.running_left = False
        # Shoots projectiles using the Player's x, y, and direction
        if keys[pg.K_p]:
            print(self.rect.x)
            p = Projectile(self.game, self.rect.x, self.rect.y, self.dir)
        # Identifies a to walk left
        if keys[pg.K_a]:
            self.vel.x = -self.speed*self.game.dt
            self.dir = vec(-1,0)
            self.running_left = True
        # Identifies d to walk right
        if keys[pg.K_d]:
            self.vel.x = self.speed*self.game.dt
            self.dir = vec(1,0)
            self.running_right = True
        # Identifies space to jump
        if keys[pg.K_SPACE]:
            self.jumping = True
        # Identifies e to search
        if keys[pg.K_e]:
            self.searching = True
        # accounting for diagonal
        if self.vel[0] != 0 and self.vel[1] != 0:
            self.vel *= 0.7071

    # If player is crouching, then the speed is slower, or else, it remains the same
    def crouch(self):
        # if crouching
        if self.crouching:
            self.speed = 75
            print("crouching")
        # if not crouching
        else:
            self.speed = 150
            print("not crouching")

    # Detects if the sprite collides with each other
    # Player collides with Wall
    def collide_with_walls(self, dir):
        # Detects collisions in the x direction (horizontally)
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
            # if the player collides
            if hits:
                # print(self.pos)
                # Detects for moveable and unmoveable blocks
                # if the player is moving right
                if self.vel.x > 0:
                    if hits[0].state == "moveable":
                        #print("i hit a moveable block...")
                        hits[0].vel.x += self.vel.x
                        if len(hits) > 1:
                            if hits[1].state in ("unmoveable", "searchable"):
                                self.pos.x = hits[1].rect.left - self.rect.width
                    else:
                        self.pos.x = hits[0].rect.left - self.rect.width
                # Detects for moveable and unmoveable blocks
                # If the object is moving left
                if self.vel.x < 0:
                    if hits[0].state == "moveable":
                        #print("i hit a moveable block...")
                        hits[0].vel.x += self.vel.x
                    else:
                        self.pos.x = hits[0].rect.right
                # Sets the player to not move and updates the position
                self.vel.x = 0
                self.rect.x = self.pos.x
        # Detects collisions in the y direction (vertically)
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
            if hits:
                # If the direction is moving down
                if self.vel.y > 0:
                    if hits[0].state == "moveable":
                        #print("i hit a moveable block...")
                        hits[0].vel.y += self.vel.y
                        if len(hits) > 1:
                            if hits[1].state in ("unmoveable", "searchable"):
                                self.pos.y = hits[1].rect.top - self.rect.height
                    else:
                        self.pos.y = hits[0].rect.top - self.rect.height
                # If the direction is moving up
                if self.vel.y < 0:
                    if hits[0].state == "moveable":
                        hits[0].vel.y += self.vel.y
                        if len(hits) > 1:
                            if hits[1].state in ("unmoveable", "searchable"):
                                self.pos.y = hits[1].rect.bottom
                    else:
                        self.pos.y = hits[0].rect.bottom
                self.vel.y = 0
                self.rect.y = self.pos.y
    
    # Detects if it collides with other sprites than walls like mob and coin
    # Terminates the sprite once the player collides with it
    def collide_with_stuff(self, group, kill):
        hits = pg.sprite.spritecollide(self, group, kill)
        if hits: 
            # Removes player health and starts a cooldown
            if str(hits[0].__class__.__name__) == "Mob":
                if self.cd.ready():
                    self.health -= 10
                    self.cd.start()
            # Adds coin
            if str(hits[0].__class__.__name__) == "Coin":
                self.coins += 1
                print(self.coins)
    # Updates player behavior, animation, and detection for collisions
    def update(self):
        self.get_keys()
        self.animate()
        self.pos += self.vel
        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        self.rect.y = self.pos.y
        self.collide_with_walls('y')
        self.collide_with_stuff(self.game.all_mobs, False)
        self.collide_with_stuff(self.game.all_coins, True)
        self.y_velocity -= GRAVITY

        # Gravity + jumping
        if self.jumping:
            # Move by current vertical velocity
            self.pos.y -= self.y_velocity
            self.rect.y = self.pos.y
            # Check for collisions with collidable walls
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
            if hits:
                # If moving up and hit a ceiling
                if self.y_velocity > 0:
                    self.y_velocity = 0
                    self.pos.y = hits[0].rect.bottom
                # If moving down and hit any floor
                else:
                    self.pos.y = hits[0].rect.top - self.rect.height
                    self.jumping = False
                    self.y_velocity = self.jump_height
            self.rect.y = self.pos.y
        # Not jumping, applying gravity (fall)
        else:
            # Sets cap on fall velocity to jump_height
            if self.y_velocity < -self.jump_height:
                self.y_velocity = -self.jump_height
            # falling
            self.pos.y += self.jump_height - self.y_velocity
            self.rect.y = self.pos.y
            # Check collisions for falling
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
            if hits:
                self.pos.y = hits[0].rect.top - self.rect.height
                self.jumping = False
                self.y_velocity = self.jump_height
            self.rect.y = self.pos.y

        '''
        if not self.cd.ready():
            #self.image = self.game.player_img_inv
            self.image = self.game.player_img
            # self.rect = self.image_inv.get_rect()
            print("not ready")
        else:
            # self.image.fill(GREEN)
            self.image = self.game.player_img
            # self.rect = self.image.get_rect()
            print("ready")
        '''
# Created under parent class Sprite
# Detects collisoins with walls
class Mob(Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.groups = game.all_sprites, game.all_mobs
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((32, 32))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.vel = vec(choice([-1,1]),choice([-1,1]))
        self.pos = vec(x,y)*TILESIZE[0]
        self.speed = 5
        print(self.pos)
    def collide_with_walls(self, dir):
        # If mob collides in the x direction (horizontal)
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
            # If collision
            if hits:
                # If the mob is moving right
                if self.vel.x > 0:
                    self.pos.x = hits[0].rect.left - self.rect.width
                # If the mob is moving left
                if self.vel.x < 0:
                    self.pos.x = hits[0].rect.right
                self.rect.x = self.pos.x
                self.vel.x *= choice([-1,1])
        # If mob collides in the y direction (vertical)
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
            # If collision
            if hits:
                # If the mob is moving down
                if self.vel.y > 0:
                    self.pos.y = hits[0].rect.top - self.rect.height
                # If the mob is moving up
                if self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom
                self.rect.y = self.pos.y
                self.vel.y *= choice([-1,1])
    # updates the position of the mob to follow the x and y coordinates of the player's
    # detects collisions with walls
    def update(self):
        # mob behavior
        if self.game.player.pos.x > self.pos.x:
            self.vel.x = 1
        else:
            self.vel.x = -1
            # print("I don't need to chase the player x")
        if self.game.player.pos.y > self.pos.y:
            self.vel.y = 1
        else:
            self.vel.y = -1
            # print("I don't need to chase the player x")
        self.pos += self.vel * self.speed
        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        self.rect.y = self.pos.y
        self.collide_with_walls('y')

# Class under parent class Sprite
# Just defines a sprite that is yellow
class Coin(Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.groups = game.all_sprites, game.all_coins
        Sprite.__init__(self, self.groups)
        self.image = pg.Surface(TILESIZE)
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE[0]
        self.rect.y = y *TILESIZE[1]
        # coin behavior
        pass

class Searchable(Sprite):
    def __init__(self, game, x, y, state):
        self.groups = game.all_sprites, game.all_searchable
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface(TILESIZE)
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.vel = vec(0,0)
        self.pos = vec(x,y) * TILESIZE[0]
        self.state = state
    def collide_with_searchable(self, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.all_searchable, False)
            # If collision
            if hits:
                # If the player is moving right
                if self.vel.x > 0:
                    if hits[0].state == "moveable":
                        hits[0].pos.x += self.vel.x
                        if len(hits) > 1:
                            if hits[1].state in ("unmoveable", "searchable"):
                                self.pos.x = hits[1].rect.left - self.rect.width
                    else:
                        self.pos.x = hits[0].rect.left - self.rect.width
                # If the player is moving left
                if self.vel.x < 0:
                    if hits[0].state == "moveable":
                        hits[0].pos.x += self.vel.x
                        if len(hits) > 1:
                            if hits[1].state in ("unmoveable", "searchable"):
                                self.pos.x = hits[1].rect.right
                    else:
                        self.pos.x = hits[0].rect.right
                self.vel.x = 0
                self.rect.x = self.pos.x
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
            if hits:
                # If the player is moving down
                if self.vel.y > 0:
                    if hits[0].state == "moveable":
                        hits[0].pos.y += self.vel.y
                        if len(hits) > 1:
                            if hits[1].state == "unmoveable":
                                self.pos.y = hits[1].rect.top - self.rect.height
                    else:
                        self.pos.y = hits[0].rect.top - self.rect.height
                # If the player is moving up
                if self.vel.y < 0:
                    if hits[0].state == "moveable":
                        hits[0].pos.y += self.vel.y
                        if len(hits) > 1:
                            if hits[1].state == "unmovable":
                                self.pos.y = hits[1].rect.bottom
                    else:
                        self.pos.y = hits[0].rect.bottom
                self.vel.y = 0
                self.rect.y = self.pos.y
    def update(self):
        # upadtes wall behavior
        self.pos += self.vel
        self.rect.x = self.pos.x
        self.collide_with_searchable('x')
        self.rect.y = self.pos.y
        self.collide_with_searchable('y')

    # Detects collisions with 
# Class under parent class Sprite
class Wall(Sprite):
    def __init__(self, game, x, y, state):
        self.groups = game.all_sprites, game.all_walls
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface(TILESIZE)
        self.image.fill(DARK_GREY)
        self.rect = self.image.get_rect()
        self.vel = vec(0,0)
        self.pos = vec(x,y) * TILESIZE[0]
        self.state = state
    # Detects collisions with moveable and unmoveable walls in the x and y direction
    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
            # If collision
            if hits:
                # If the player is moving right
                if self.vel.x > 0:
                    if hits[0].state == "moveable":
                        hits[0].pos.x += self.vel.x
                        if len(hits) > 1:
                            if hits[1].state in ("unmoveable", "searchable"):
                                self.pos.x = hits[1].rect.left - self.rect.width
                    else:
                        self.pos.x = hits[0].rect.left - self.rect.width
                # If the player is moving left
                if self.vel.x < 0:
                    if hits[0].state == "moveable":
                        hits[0].pos.x += self.vel.x
                        if len(hits) > 1:
                            if hits[1].state in ("unmoveable", "searchable"):
                                self.pos.x = hits[1].rect.right
                    else:
                        self.pos.x = hits[0].rect.right
                self.vel.x = 0
                self.rect.x = self.pos.x
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
            if hits:
                # If the player is moving down
                if self.vel.y > 0:
                    if hits[0].state == "moveable":
                        hits[0].pos.y += self.vel.y
                        if len(hits) > 1:
                            if hits[1].state == "unmoveable":
                                self.pos.y = hits[1].rect.top - self.rect.height
                    else:
                        self.pos.y = hits[0].rect.top - self.rect.height
                # If the player is moving up
                if self.vel.y < 0:
                    if hits[0].state == "moveable":
                        hits[0].pos.y += self.vel.y
                        if len(hits) > 1:
                            if hits[1].state == "unmovable":
                                self.pos.y = hits[1].rect.bottom
                    else:
                        self.pos.y = hits[0].rect.bottom
                self.vel.y = 0
                self.rect.y = self.pos.y
    def update(self):
        # upadtes wall behavior
        self.pos += self.vel
        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        self.rect.y = self.pos.y
        self.collide_with_walls('y')

# Creates a sprite to have the same coordinates/position of the player
class Sword(Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.groups = game.all_sprites, game.all_swords
        Sprite.__init__(self, self.groups)
        self.image = pg.Surface(TILESIZE)
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE[0]
        self.rect.y = y * TILESIZE[1]
    # Sword tracks the player's rect position
    def update(self):
        self.rect.x = self.game.player.rect.x
        self.rect.y = self.game.player.rect.y

# Class under parent class Sprite
class Projectile(Sprite):
    def __init__(self, game, x, y, dir):
        self.game = game
        self.groups = game.all_sprites, game.all_projectiles
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((16, 16))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.vel = dir
        self.pos = vec(x,y)
        self.rect.x = x
        self.rect.y = y
        self.speed = 10
    # updates the Projectile velocity and direction
    def update(self):
        self.pos += self.vel * self.speed
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        hits = pg.sprite.spritecollide(self, self.game.all_walls, True)
        # if collision, then destroy the wall
        if hits:
            self.kill()
        
