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
# Used help from ChatGPT with jumping and uncrouching method (debugging the hitboxes)

# Class under parent class Sprite
# Defines a new sprite that the player can control based off key inputs
# Collisions will be detected (walls and coins)
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

        self.jump_height = 20
        self.y_velocity = self.jump_height
        self.PLAYER_WIDTH = 43
        self.PLAYER_STAND_HEIGHT = 64
        self.PLAYER_CROUCH_HEIGHT = 43

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
            frame = self.spritesheet_crouch_idle.get_image(0, i * 43, 43, 43)
            frame.set_colorkey(BLACK)
            self.crouching_frames_idle.append(frame)

        # Loops throughout the running animation png and appends a frame into a list
        # Calls list to get each image
        self.crouching_frames_right = []
        for i in range(4):
            frame = self.spritesheet_crouch_right.get_image(0, i * 43, 43, 43)
            frame.set_colorkey(BLACK)
            self.crouching_frames_right.append(frame)
        
        # Loops throughout the running animation png and appends a frame into a list
        # Calls list to get each image
        self.crouching_frames_left = []
        for i in range(4):
            frame = self.spritesheet_crouch_left.get_image(0, i * 43, 43, 43)
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
    
    # Identifies the keys the user inputs and moves the player accordingly
    def get_keys(self):
        self.vel = vec(0,0)
        keys = pg.key.get_pressed()
        self.running_right = False
        self.running_left = False
        
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
        if self.crouching:
            self.rect.height = self.PLAYER_CROUCH_HEIGHT
            self.speed = 75
            self.rect.bottom = self.pos.y
            
    # if not crouching
    def try_uncrouch(self):
        # Fake rect that mimics the hitbox of a standing player
        test_rect = pg.Rect(
            self.rect.x,
            self.rect.bottom - self.PLAYER_STAND_HEIGHT,
            self.PLAYER_WIDTH,
            self.PLAYER_STAND_HEIGHT
        )

        # If there is not enough space on top for the player to uncrouch, stay crouched
        for wall in self.game.all_walls:
            if test_rect.colliderect(wall.rect):
                return

        # Safe to stand
        self.crouching = False
        self.rect.height = self.PLAYER_STAND_HEIGHT
        self.rect.bottom = self.pos.y
        self.speed = 150


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
        # Not a method to not allow for spam jumping in the air
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


# Created under parent class Sprite
# Detects collisions with walls
class Mob(Sprite):
    def __init__(self, game, x, y, patrol_dist=200):
        self.game = game
        self.groups = game.all_sprites, game.all_mobs
        Sprite.__init__(self, self.groups)

        self.image = pg.Surface((32, 32))
        self.image.fill(RED)
        self.rect = self.image.get_rect()

        self.pos = vec(x, y) * TILESIZE[0]
        self.rect.topleft = self.pos

        # Patrol (A to B Path Finding)
        self.start_x = self.pos.x
        self.end_x = self.pos.x + patrol_dist
        self.direction = 1   # 1 = right, -1 = left
        self.speed = 2

        # Gravity
        self.y_velocity = 0  # vertical velocity

        # Vision
        self.vision_length = 150
        self.vision_angle = 40  # degrees

    # Collision detection with walls
    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
            if hits:
                if self.direction > 0:  # moving right
                    self.pos.x = hits[0].rect.left - self.rect.width
                elif self.direction < 0:  # moving left
                    self.pos.x = hits[0].rect.right
                self.rect.x = self.pos.x
                # Reverse direction on collision
                self.direction *= -1

        elif dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
            if hits:
                if self.y_velocity > 0:  # falling
                    self.pos.y = hits[0].rect.top - self.rect.height
                    self.y_velocity = 0
                elif self.y_velocity < 0:  # moving up
                    self.pos.y = hits[0].rect.bottom
                    self.y_velocity = 0
                self.rect.y = self.pos.y

    # Patrol behavior and gravity
    def update(self):
        # Patrol horizontally
        self.pos.x += self.direction * self.speed
        self.rect.x = self.pos.x
        self.collide_with_walls('x')

        # Gravity
        self.y_velocity += GRAVITY
        self.pos.y += self.y_velocity
        self.rect.y = self.pos.y
        self.collide_with_walls('y')

        # Reverse direction at patrol edges
        if self.pos.x >= self.end_x:
            self.direction = -1
        elif self.pos.x <= self.start_x:
            self.direction = 1

        # Optional: check if mob can see player
        if self.can_see_player():
            print("PLAYER SPOTTED")

    # Check if player is inside mob's vision
    def can_see_player(self):
        self.player_vec = vec(self.game.player.rect.center) - vec(self.rect.center)
        self.distance = self.player_vec.length()
        if self.distance > self.vision_length:
            return False
        self.facing = vec(self.direction, 0)
        if self.facing.length() == 0:
            return False
        self.angle = self.facing.angle_to(self.player_vec)
        return abs(self.angle) < self.vision_angle / 2

    # Draw vision triangle (flashlight)
    def draw_vision(self, surface):
        self.temp_surf = pg.Surface((surface.get_width(), surface.get_height()), pg.SRCALPHA)
        self.start = vec(self.rect.center)
        self.facing = vec(self.direction or 1, 0).normalize()
        self.left_dir = self.facing.rotate(self.vision_angle / 2)
        self.right_dir = self.facing.rotate(-self.vision_angle / 2)
        self.points = [self.start, self.start + self.left_dir * self.vision_length, self.start + self.right_dir * self.vision_length]
        self.points = [(int(p.x), int(p.y)) for p in self.points]
        pg.draw.polygon(self.temp_surf, (255, 255, 0, 75), self.points)
        surface.blit(self.temp_surf, (0, 0))



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
