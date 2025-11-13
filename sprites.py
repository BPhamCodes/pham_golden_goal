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

# Class under parent class Sprite
# Defines a new sprite that the player can control based off key inputs
# Collisions will be detected (walls, coins, and ball(s))
class Player(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.spritesheet = Spritesheet(path.join(self.game.img_folder, "spritesheet.png"))
        self.spritesheet_anim = Spritesheet(path.join(self.game.img_folder, "spritesheet_anim.png"))
        self.spritesheet_anim2 = Spritesheet(path.join(self.game.img_folder, "spritesheet_anim2.png"))
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
        self.walking = False
        self.jumping = False
        self.running_right = False
        self.running_left = False
        self.attacking = False
        self.current_frame = 0
        self.last_update = 0

        self.jump_height = 20
        self.y_velocity = self.jump_height
        self.jumping = False

    # loads images for the idle and running frames
    def load_images(self):
        # Loops throughout the idle animation png and appends a frame into a list
        # Calls list to get each image
        self.standing_frames = [
            self.spritesheet.get_image(0, 0, 64, 64),
            self.spritesheet.get_image(0, 64, 64, 64)]
        for frame in self.standing_frames:
            frame.set_colorkey(BLACK)

        # Loops throughout the running animation png (right) and appends a frame into a list
        # Calls list to get each image
        self.running_frames_right = []
        for i in range(10):
            frame = self.spritesheet_anim.get_image(0, i * 64, 64, 64)
            frame.set_colorkey(BLACK)
            self.running_frames_right.append(frame)
        
        # Loops throughout the running animation png (left) and appends a frame into a list
        # Calls list to get each image
        self.running_frames_left = []
        for i in range(10):
            frame = self.spritesheet_anim2.get_image(0, i * 64, 64, 64)
            frame.set_colorkey(BLACK)
            self.running_frames_left.append(frame)

    # Creates the animations for the idle and running
    def animate(self):
        now = pg.time.get_ticks()
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
        if self.running_right:
            if now - self.last_update > 50:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.running_frames_right)
                bottom = self.rect.bottom
                self.image = self.running_frames_right[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        # creates the running animatoin if the player is moving left
        # With time per frame
        if self.running_left:
            if now - self.last_update > 50:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.running_frames_left)
                bottom = self.rect.bottom
                self.image = self.running_frames_left[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
    def attack(self):
        if not self.attacking and self.weapon_cd.ready():
            self.weapon_cd.start()
            self.attacking = True
            print ("attacking")
            self.weapon = Sword(self.game, self.rect.x, self.rect.y)
    # Identifies the keys the user inputs and moves the player accordingly
    def get_keys(self):
        self.vel = vec(0,0)
        keys = pg.key.get_pressed()
        self.running_right = False
        self.running_left = False
        # Shoots projectiles using the Player's x, y, and direction
        #if keys[pg.K_SPACE]:
           # print(self.rect.x)
           # p = Projectile(self.game, self.rect.x, self.rect.y, self.dir)

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
        # accounting for diagonal
        if self.vel[0] != 0 and self.vel[1] != 0:
            self.vel *= 0.7071
    def attack(self):
        if self.attacking and self.weapon_cd.ready():
            self.weapon_cd.start()
            self.attacking = True
            print ("attacking")
            #rect.kill()
            self.attacking = False

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
                            if hits[1].state == "unmoveable":
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
                            if hits[1].state == "unmoveable":
                                self.pos.y = hits[1].rect.top - self.rect.height
                    else:
                        self.pos.y = hits[0].rect.top - self.rect.height
                # If the direction is moving up
                if self.vel.y < 0:
                    if hits[0].state == "moveable":
                        hits[0].vel.y += self.vel.y
                        if len(hits) > 1:
                            if hits[1].state == "unmovable":
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
    
# Class under parent class Sprite
class Wall(Sprite):
    def __init__(self, game, x, y, state):
        self.groups = game.all_sprites, game.all_walls
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface(TILESIZE)
        self.image.fill(GREEN)
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
                            if hits[1].state == "unmoveable":
                                self.pos.x = hits[1].rect.left - self.rect.width
                    else:
                        self.pos.x = hits[0].rect.left - self.rect.width
                # If the player is moving left
                if self.vel.x < 0:
                    if hits[0].state == "moveable":
                        hits[0].pos.x += self.vel.x
                        if len(hits) > 1:
                            if hits[1].state == "unmoveable":
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

'''
# Class under parent class Sprite
class MoveableBall(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_moveable_balls
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.ball_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.pos = vec(x, y) * TILESIZE[0]
        self.rect.topleft = self.pos
        self.vel = vec(randint(-3, 3), randint(-3, 3))
        self.state = "moveable"

    # If the ball's left or right side overlaps the edge of the screen's width and height,
    # then the ball bounces back by changing the vector in the opposite direction
    def collide_with_edges(self):
        # Bounces off screen's sides by checking collisions
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.vel.x *= BOUNCE
            self.rect.x = max(0, min(self.rect.x, WIDTH - self.rect.width))
            self.pos.x = self.rect.x
        # Bounces with screen's top or bottom by checking collisions
        if self.rect.top < 0 or self.rect.bottom > HEIGHT:
            self.vel.y *= BOUNCE
            self.rect.y = max(0, min(self.rect.y, HEIGHT - self.rect.height))
            self.pos.y = self.rect.y

    # Detects collisions with walls
    def collide_with_walls(self):
        # Bounce off of unmoveable walls
        hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
        for hit in hits:
            if hit.state == "unmoveable":
                # All of these if conditions assumes that if the ball is less than 25 pixels away from the wall
                # then, this is considered a collision to account for possible frameskips that cause the ball to phase through
                if abs(self.rect.right - hit.rect.left) < 25 and self.vel.x > 0:
                    self.rect.right = hit.rect.left
                    self.vel.x *= BOUNCE
                if abs(self.rect.left - hit.rect.right) < 25 and self.vel.x < 0:
                    self.rect.left = hit.rect.right
                    self.vel.x *= BOUNCE
                if abs(self.rect.bottom - hit.rect.top) < 25 and self.vel.y > 0:
                    self.rect.bottom = hit.rect.top
                    self.vel.y *= BOUNCE
                if abs(self.rect.top - hit.rect.bottom) < 25 and self.vel.y < 0:
                    self.rect.top = hit.rect.bottom
                    self.vel.y *= BOUNCE
                # updates ball position
                self.pos = vec(self.rect.topleft)
                
    # Initializes the player
    # measures the dfference between the player and the ball
    def collide_with_player(self):
        player = self.game.player
        if self.rect.colliderect(player.rect):
            # difference in coordinates from player to ball
            self.diff_pos_player = self.pos - player.pos
            if self.diff_pos_player == (0, 0):
                self.diff_pos_player = vec(1, 0)
            # Normalize the difference to get the direction, not the distance
            self.diff_pos_player = self.diff_pos_player.normalize()

            # Pushes ball away from player; stronger if player is moving faster
            impact_strength = player.vel.length() + 5
            self.vel += self.diff_pos_player * impact_strength

            # Knockback for player
            player.pos -= self.diff_pos_player * 5
            player.rect.topleft = player.pos
    # Updates ball behavior
    def update(self):
        self.pos += self.vel
        self.rect.topleft = self.pos

        self.collide_with_edges()
        self.collide_with_walls()
        self.collide_with_player()

        # Apply friction
        self.vel *= FRICTION
        # Makes the ball eventaully stop
        if self.vel.length() < 0.1:
            self.vel = vec(0, 0)
'''
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
        
