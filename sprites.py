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
import math
vec = pg.math.Vector2

# https://www.youtube.com/watch?v=ST-Qq3WBZBE: source to add jump
# Used help from ChatGPT with uncrouching method (debugging the hitboxes) and can_see_player() method in Mob class

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
        
        self.flash_duration = 500   # milliseconds
        self.last_damage_time = 0


        self.jump_height = 20
        self.y_velocity = self.jump_height
        self.PLAYER_WIDTH = 43
        self.PLAYER_STAND_HEIGHT = 64
        self.PLAYER_CROUCH_HEIGHT = 43
        self.PLAYER_STAND_WIDTH = 64

        self.inventory = []

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
        if self.crouching and not self.running_right and not self.running_left and not self.jumping:
            if now - self.last_update > 250:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.crouching_frames_idle)
                bottom = self.rect.bottom
                self.image = self.crouching_frames_idle[self.current_frame]

                left = self.rect.left
                bottom = self.rect.bottom
                self.rect = self.image.get_rect()
                self.rect.left = left
                self.rect.bottom = bottom

        # creates the running animation if the player is idle
        if not self.jumping and not self.walking:
            if now - self.last_update > 250:
                # print(now)
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                
                left = self.rect.left
                bottom = self.rect.bottom
                self.rect = self.image.get_rect()
                self.rect.left = left
                self.rect.bottom = bottom

        # creates the running animation if the player is moving right
        # With time per frame
        if self.running_right and not self.jumping and not self.crouching:
            if now - self.last_update > 50:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.running_frames_right)
                bottom = self.rect.bottom
                self.image = self.running_frames_right[self.current_frame]
                
                left = self.rect.left
                bottom = self.rect.bottom
                self.rect = self.image.get_rect()
                self.rect.left = left
                self.rect.bottom = bottom
        # creates the running animation if the player is moving left
        # With time per frame
        if self.running_left and not self.jumping and not self.crouching:
            if now - self.last_update > 50:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.running_frames_left)
                bottom = self.rect.bottom
                self.image = self.running_frames_left[self.current_frame]
                
                left = self.rect.left
                bottom = self.rect.bottom
                self.rect = self.image.get_rect()
                self.rect.left = left
                self.rect.bottom = bottom
        # creates the jumping animation if the player is moving left and is jumping
        # With time per frame
        if self.jumping and self.running_left:
            if now - self.last_update > 200:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.jumping_frames_left)
                bottom = self.rect.bottom
                self.image = self.jumping_frames_left[self.current_frame]
                
                left = self.rect.left
                bottom = self.rect.bottom
                self.rect = self.image.get_rect()
                self.rect.left = left
                self.rect.bottom = bottom
        # creates the running animation if the player is moving right and jumping, or is just jumping
        # With time per frame
        if ((self.jumping and self.running_right) or self.jumping):
            if now - self.last_update > 200:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.jumping_frames_right)
                bottom = self.rect.bottom
                self.image = self.jumping_frames_right[self.current_frame]
                
                left = self.rect.left
                bottom = self.rect.bottom
                self.rect = self.image.get_rect()
                self.rect.left = left
                self.rect.bottom = bottom
        # creates the running animation if the player is crouching and walking right
        # With time per frame
        if self.crouching and self.running_right:
            if now - self.last_update > 200:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.crouching_frames_right)
                bottom = self.rect.bottom
                self.image = self.crouching_frames_right[self.current_frame]
                
                left = self.rect.left
                bottom = self.rect.bottom
                self.rect = self.image.get_rect()
                self.rect.left = left
                self.rect.bottom = bottom
        # creates the running animation if the player is crouching and walking left
        # With time per frame
        if self.crouching and self.running_left:
            if now - self.last_update > 200:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.crouching_frames_left)
                bottom = self.rect.bottom
                self.image = self.crouching_frames_left[self.current_frame]
                
                left = self.rect.left
                bottom = self.rect.bottom
                self.rect = self.image.get_rect()
                self.rect.left = left
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
            if not self.crouching and self.can_uncrouch():
                self.jumping = True
        # Identifies e to search
        if keys[pg.K_e]:
            self.searching = True
        # accounting for diagonal
        if self.vel[0] != 0 and self.vel[1] != 0:
            self.vel *= 0.7071

    # If player is crouching, then the speed is slower, or else, it remains the same
    def crouch(self):
        if self.jumping:
            return
        self.rect.height = self.PLAYER_CROUCH_HEIGHT
        bottom = self.rect.bottom
        self.rect.bottom = bottom  # restore feet
        self.speed = 75
 
    # if not crouching
    def try_uncrouch(self):
        # Fake rect that mimics the hitbox of a standing player
        test_rect = pg.Rect(self.rect.x, self.rect.bottom - self.PLAYER_STAND_HEIGHT, self.PLAYER_STAND_WIDTH, self.PLAYER_STAND_HEIGHT)

        for wall in self.game.all_walls:
            if test_rect.colliderect(wall.rect):
                return

        # Safe to stand
        bottom = self.rect.bottom
        self.crouching = False
        self.rect.height = self.PLAYER_STAND_HEIGHT
        self.rect.bottom = bottom
        self.speed = 150

    def can_uncrouch(self):
        test_rect = pg.Rect(self.rect.x, self.rect.bottom - self.PLAYER_STAND_HEIGHT, self.PLAYER_STAND_WIDTH, self.PLAYER_STAND_HEIGHT)

        for wall in self.game.all_walls:
            if test_rect.colliderect(wall.rect):
                return False
        return True

    def has_screwdriver(self):
        return any(getattr(item, 'name', '') == 'screwdriver' for item in self.inventory)

    def has_crowbar(self):
        return any(getattr(item, 'name', '') == 'crowbar' for item in self.inventory)
    


    # Detects if the sprite collides with each other
    # Player collides with Wall
    def collide_with_walls(self, dir):
        # Detects collisions in the x direction (horizontally)
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
            if hits:
                for hit in hits:
                    # Destroy vent if player has screwdriver AND is crouching
                    if hit.state == "vent" and self.has_screwdriver() and self.crouching:
                        hit.kill()
                        continue  # skip further collision processing for this vent
                    # Inside Player.collide_with_walls, where you check for vent
                    # Destroy box if has crowbar 
                    if hit.state == "box" and self.has_crowbar():
                        hit.destroy()  # uses destroy() method to drop key if applicable
                        continue  # skip further collision processing
                    # Destroy door if player has a key
                    if hit.state == "door":
                        if any(getattr(item, 'name', '') == 'key' for item in self.inventory):
                            hit.kill()
                            continue
                    # Existing collision logic
                    if self.vel.x > 0:  # moving right
                        if hit.state == "moveable":
                            hit.vel.x += self.vel.x
                        else:
                            self.pos.x = hit.rect.left - self.rect.width
                    if self.vel.x < 0:  # moving left
                        if hit.state == "moveable":
                            hit.vel.x += self.vel.x
                        else:
                            self.pos.x = hit.rect.right
                self.vel.x = 0
                self.rect.x = self.pos.x

        # Detects collisions in the y direction (vertically)
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
            if hits:
                for hit in hits:
                    # Destroy vent if player has screwdriver AND is crouching
                    if hit.state == "vent" and self.has_screwdriver() and self.crouching:
                        hit.kill()
                        continue  # skip further collision processing for this vent
                    if hit.state == "box" and self.has_crowbar():
                        hit.destroy()  # uses destroy() method to drop key if applicable
                        continue  # skip further collision processing
                    # Destroy door if player has a key
                    if hit.state == "door":
                        if any(getattr(item, 'name', '') == 'key' for item in self.inventory):
                            hit.kill()
                            continue
                    # Existing collision logic
                    if self.vel.y > 0:  # moving down
                        if hit.state == "moveable":
                            hit.vel.y += self.vel.y
                        else:
                            self.pos.y = hit.rect.top - self.rect.height
                    if self.vel.y < 0:  # moving up
                        if hit.state == "moveable":
                            hit.vel.y += self.vel.y
                        else:
                            self.pos.y = hit.rect.bottom
                self.vel.y = 0
                self.rect.y = self.pos.y


    # Detects if it collides with other sprites than walls like mob and coin
    # Terminates the sprite once the player collides with it
    def collide_with_stuff(self, group, kill):
        hits = pg.sprite.spritecollide(self, group, kill)
        if hits:
            if isinstance(hits[0], Screwdriver):
                self.inventory.append(hits[0])
            if isinstance(hits[0], Crowbar):
                self.inventory.append(hits[0])
            if isinstance(hits[0], Key):
                self.inventory.append(hits[0])
            


    # Adds a health bar using the percentage of the player's current health from the original
    def draw_health_bar(self, surface):
        # Position and size
        bar_width = 200
        bar_height = 20
        x = 50  # left margin
        y = 50  # top margin
        # Calculate health percentage
        health_percent = max(self.health / 100, 0)
        # Background (grey)
        bg_rect = pg.Rect(x, y, bar_width, bar_height)
        pg.draw.rect(surface, DARK_GREY, bg_rect)
        # Health fill (green)
        fg_rect = pg.Rect(x, y, bar_width * health_percent, bar_height)
        now = pg.time.get_ticks()
        # Flash red if within 500ms after taking damage
        if now - self.last_damage_time <= self.flash_duration:
            color = RED
        # Stay green for every other instance
        else:
            color = GREEN
        pg.draw.rect(surface, color, fg_rect)
        # border
        pg.draw.rect(surface, WHITE, bg_rect, 2)

    # draws inventory at tjhe bottom of the screen
    def draw_inventory(self, surface):
        self.icon_size = 64
        self.padding = 10

        start_x = self.padding
        y = surface.get_height() - self.icon_size - self.padding

        # enumerates through inventory and displays anything on the bottom left of the screen
        for i, item in enumerate(self.inventory):
            icon = pg.transform.scale(item.inventory_image, (self.icon_size, self.icon_size))
            x = start_x + i * (self.icon_size + self.padding)
            surface.blit(icon, (x, y))
    

    # Updates player behavior, animation, and detection for collisions
    def update(self):
        # Keep the player from updating during level transition
        if self.game.transitioning:
            return

        self.get_keys()
        self.animate()
        self.pos += self.vel
        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        self.rect.y = self.pos.y
        self.collide_with_walls('y')
        self.collide_with_stuff(self.game.all_mobs, False)
        self.collide_with_stuff(self.game.all_items, True)
        self.y_velocity -= GRAVITY
        # HARD SAFETY: prevent jumping if crouched with no headroom
        if self.jumping and self.crouching and not self.can_uncrouch():
            self.jumping = False
        keys = pg.key.get_pressed()
        if self.crouching and not keys[pg.K_LCTRL] and self.can_uncrouch():
            self.try_uncrouch()
        
        if self.health <= 0:
            self.player_died()
        
        if self.game.time == 0:
            self.player_died()
            
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
            
        # Check if player leaves the map on the LEFT side
        tile_x = int(self.pos.x // TILESIZE[0])

        if tile_x < 0 and not self.game.transitioning:
            self.game.transitioning = True
            self.game.map_state += 1
            self.game.playing = False
            if self.game.map_state == 4:
                # Fill the screen with black or red
                self.game.screen.fill(BLACK)
                font = pg.font.SysFont("ArcadeClassic", 72)
                text = font.render("VICTORY", True, YELLOW)
                text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
                self.game.screen.blit(text, text_rect)
                self.health = 100
                pg.display.flip()

                # Wait 3 seconds
                pg.time.delay(3000)
                
                # Quit game
                pg.quit()
                exit()

    # Player death
    def player_died(self):
        # Fill the screen with black or red
        self.game.screen.fill(BLACK)
        font = pg.font.SysFont("ArcadeClassic", 72)
        text = font.render("YOU DIED", True, RED)
        text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.game.screen.blit(text, text_rect)
        pg.display.flip()

        # Wait 3 seconds
        pg.time.delay(3000)
        
        # Quit game
        pg.quit()
        exit()


# Created under parent class Sprite
# Detects collisions with walls
class Mob(Sprite):
    def __init__(self, game, x, y, patrol_dist=250):
        self.game = game
        self.groups = game.all_sprites, game.all_mobs
        Sprite.__init__(self, self.groups)

        self.image = pg.Surface((64, 64))
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

        self.damage_cd = Cooldown(1000)
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

        # check if mob can see player
        if self.can_see_player():
            if self.damage_cd.ready():
                self.game.player.health -= 20
                self.game.player.last_damage_time = pg.time.get_ticks()
                self.damage_cd.start()

    def can_see_player(self):
        # Vector from mob to player
        self.to_player = vec(self.game.player.rect.center) - vec(self.rect.center)
        self.distance = self.to_player.length()

        # If the player is too far away from the mob's visibility
        if self.distance == 0 or self.distance > self.vision_length:
            return False

        # Finds direction, not distance
        self.to_player.normalize_ip()

        # Mob facing direction
        self.facing = vec(self.direction, 0)
        if self.facing.length() == 0:
            # default facing right
            self.facing = vec(1, 0)
        self.facing.normalize_ip()

        # Dot product gives cosine of angle between vectors
        self.dot = self.facing.dot(self.to_player)

        # Convert vision angle to cosine threshold
        self.vision_cos = math.cos(math.radians(self.vision_angle / 2))

        return self.dot >= self.vision_cos

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
# Defines a collectible screwdriver item
class Screwdriver(Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.groups = game.all_sprites, game.all_items
        Sprite.__init__(self, self.groups)
        self.name = "screwdriver"

        # World (map) sprite
        self.image = pg.image.load(path.join(self.game.img_folder, "screwdriver_world.png")).convert_alpha()
        self.image.set_colorkey(BLACK)
        
        # Inventory icon (UI)
        self.inventory_image = pg.image.load(path.join(self.game.img_folder, "screwdriver_inventory.png")).convert_alpha()
        self.inventory_image.set_colorkey(BLACK)
        
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE[0]
        self.rect.y = y * TILESIZE[1]

# Class under parent class Sprite
# Defines a collectible crowbar item
class Crowbar(Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.groups = game.all_sprites, game.all_items
        Sprite.__init__(self, self.groups)
        self.name = "crowbar"

        # World (map) sprite
        self.image = pg.image.load(path.join(self.game.img_folder, "crowbar_world.png")).convert_alpha()
        self.image.set_colorkey(BLACK)
        
        # Inventory icon (UI)
        self.inventory_image = pg.image.load(path.join(self.game.img_folder, "crowbar_inventory.png")).convert_alpha()
        self.inventory_image.set_colorkey(BLACK)
        
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE[0]
        self.rect.y = y * TILESIZE[1]

# Class under parent class Sprite
# Defines an unmoveable vent that only allows passage
# if the player has at least one screwdriver
class Vent(Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.groups = game.all_sprites, game.all_walls
        Sprite.__init__(self, self.groups)

        # Vent sprite image
        self.image = pg.image.load(path.join(self.game.img_folder, "vent.png")).convert_alpha()

        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE[0]
        self.rect.y = y * TILESIZE[1]

        # Identifies this wall as a vent
        self.state = "vent"

        # Vent does not move
        self.vel = vec(0, 0)
        self.pos = vec(self.rect.x, self.rect.y)

    def update(self):
        # Vent is static; nothing updates
        pass

# Class under parent class Sprite
# Defines a collectible key item
class Key(Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.groups = game.all_sprites, game.all_items
        Sprite.__init__(self, self.groups)
        self.name = "key"

        # World (map) sprite
        self.image = pg.image.load(path.join(self.game.img_folder, "key_world.png")).convert_alpha()
        self.image.set_colorkey(BLACK)
        
        # Inventory icon (UI)
        self.inventory_image = pg.image.load(path.join(self.game.img_folder, "key_inventory.png")).convert_alpha()
        self.inventory_image.set_colorkey(BLACK)
        
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE[0]
        self.rect.y = y * TILESIZE[1]


# Class under parent class Sprite
# Updated Box class to optionally drop a key
class Box(Sprite):
    def __init__(self, game, x, y, drops_key=False):
        self.game = game
        self.groups = game.all_sprites, game.all_walls
        Sprite.__init__(self, self.groups)

        # Box sprite image
        self.image = pg.image.load(path.join(self.game.img_folder, "box.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE[0]
        self.rect.y = y * TILESIZE[1]

        self.state = "box"
        self.vel = vec(0, 0)
        self.pos = vec(self.rect.x, self.rect.y)

        self.drops_key = drops_key  # Controls if it drops a key

    def destroy(self):
        if self.drops_key:
            Key(self.game, self.rect.x // TILESIZE[0], self.rect.y // TILESIZE[1])
        self.kill()

# Class under parent class Sprite
# Defines a door that requires a key to open/destroy
class Door(Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.groups = game.all_sprites, game.all_walls
        Sprite.__init__(self, self.groups)

        # Load door image and scale to 1 tile width, 2 tiles height
        self.image = pg.image.load(path.join(self.game.img_folder, "door.png")).convert_alpha()
        self.image = pg.transform.scale(self.image, (TILESIZE[0], TILESIZE[1] * 2))
        
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE[0]
        self.rect.y = y * TILESIZE[1]

        self.state = "door"
        self.vel = vec(0, 0)
        self.pos = vec(self.rect.x, self.rect.y)

    def update(self):
        # Doors are static; nothing moves
        pass

# Class under parent class Sprite
# A door-like decoration that does not block the player
class Lastdoor(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game

        # Load door image and scale to same size as regular Door
        self.image = pg.image.load(path.join(self.game.img_folder, "lastdoor.png")).convert_alpha()
        self.image = pg.transform.scale(self.image, (TILESIZE[0], TILESIZE[1] * 2))

        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE[0]
        self.rect.y = y * TILESIZE[1]

        # Optional: track position if needed for animations
        self.pos = vec(self.rect.x, self.rect.y)

    def update(self):
        # Fake door is purely visual, no collisions or logic
        pass

    # Method to attempt opening the door
    def try_open(self, player):
        if any(getattr(item, 'name', '') == 'key' for item in player.inventory):
            self.kill()  # Remove the door if player has a key

# Class under parent clas Sprite
# Spotlight for player to dodge
class Spotlight(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        # Width in tiles: 3 horizontal tiles
        self.width = TILESIZE[0] * 3
        self.height = TILESIZE[1] * 2  # 2 vertical tiles

        # Create a surface with transparency
        self.image = pg.Surface((self.width, self.height), pg.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * TILESIZE[0], y * TILESIZE[1])

        self.flicker_timer = 0
        self.flicker_interval = 1500  # milliseconds
        self.on = True  # spotlight initially on

        # Triangle points for the spotlight
        self.triangle = [
            (self.width // 2, 0),  # peak at top center
            (0, self.height),      # bottom left
            (self.width, self.height)  # bottom right
        ]

        # Cooldown to prevent spamming health loss
        self.damage_cd = Cooldown(1000)  # 1 second cooldown

    def update(self):
        now = pg.time.get_ticks()
        if now - self.flicker_timer > self.flicker_interval:
            self.on = not self.on
            self.flicker_timer = now

        # Clear surface
        self.image.fill((0, 0, 0, 0))
        if self.on:
            pg.draw.polygon(self.image, (255, 255, 0, 128), self.triangle)

        # Check collision with player
        if self.on and self.rect.colliderect(self.game.player.rect):
            # Cooldown, damages player 10 if collision
            if self.damage_cd.ready():
                self.game.player.health -= 10
                self.game.player.last_damage_time = pg.time.get_ticks()
                self.damage_cd.start()


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
