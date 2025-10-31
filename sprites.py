# File created by: Brendon Pham

# The sprites module contains all the sprites
# Sprites include: player, mob - moving object


import pygame as pg
from pygame.sprite import Sprite
from settings import *
from utils import Cooldown
from utils import Spritesheet
from random import randint
from random import choice
from os import path
vec = pg.math.Vector2

class Player(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.spritesheet = Spritesheet(path.join(self.game.img_folder, "spritesheet2.png"))
        self.load_images()
        self.image = pg.Surface((32, 32))

        # self.image = game.player_img
        # self.image.set_colorkey(BLACK)
        #self.image_inv = game.player_img_inv
        self.rect = self.image.get_rect()
        self.vel = vec(0,0)
        self.pos = vec(x,y) * TILESIZE[0]
        self.speed = 250
        self.health = 100
        self.coins = 0
        self.cd = Cooldown(1000)
        self.dir = vec(0,0)
        self.walking = False
        self.jumping = False
        self.running_right = False
        self.current_frame = 0
        self.last_update = 0
    # loads images for the idle and running frames
    def load_images(self):
        self.standing_frames = [self.spritesheet.get_image(0, 0, 64, 64),
                                self.spritesheet.get_image(0, 64, 64, 64)]
        for frame in self.standing_frames:
            frame.set_colorkey(BLACK)
        # self.walk_frames_r
        # self.walk_frames_l
        # pg.transform.flip

    # Creates the animations for the idle and running
    def animate(self):
        now = pg.time.get_ticks()
        if not self.jumping and not self.walking:
            if now - self.last_update > 350:
                # print(now)
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        if self.running_right:
            pass
        
    # Identifies the keys the user inputs and moves the player accordingly
    def get_keys(self):
        self.vel = vec(0,0)
        keys = pg.key.get_pressed()
        self.running_right = False
        if keys[pg.K_SPACE]:
            print(self.rect.x)
            p = Projectile(self.game, self.rect.x, self.rect.y, self.dir)
        if keys[pg.K_w]:
            self.vel.y = -self.speed*self.game.dt
            self.dir = vec(0,-1)
        if keys[pg.K_a]:
            self.vel.x = -self.speed*self.game.dt
            self.dir = vec(-1,0)
        if keys[pg.K_s]:
            self.vel.y = self.speed*self.game.dt
            self.dir = vec(0,1)
        if keys[pg.K_d]:
            self.vel.x = self.speed*self.game.dt
            self.dir = vec(1,0)
            self.running_right = True
        # accounting for diagonal
        if self.vel[0] != 0 and self.vel[1] != 0:
            self.vel *= 0.7071
    
        
    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
            if hits:
                # print(self.pos)
                if self.vel.x > 0:
                    if hits[0].state == "moveable":
                        print("i hit a moveable block...")
                        hits[0].vel.x += self.vel.x
                        if len(hits) > 1:
                            if hits[1].state == "unmoveable":
                                self.pos.x = hits[1].rect.left - self.rect.width
                    else:
                        self.pos.x = hits[0].rect.left - self.rect.width
                        
                if self.vel.x < 0:
                    if hits[0].state == "moveable":
                        print("i hit a moveable block...")
                        hits[0].vel.x += self.vel.x
                    else:
                        self.pos.x = hits[0].rect.right
                self.vel.x = 0
                # hits[0].vel.x = 0
                self.rect.x = self.pos.x
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
            if hits:
                # print(self.pos)
                if self.vel.y > 0:
                    if hits[0].state == "moveable":
                        print("i hit a moveable block...")
                        hits[0].vel.y += self.vel.y
                        if len(hits) > 1:
                            if hits[1].state == "unmoveable":
                                self.pos.y = hits[1].rect.top - self.rect.height
                    else:
                        self.pos.y = hits[0].rect.top - self.rect.height
                        
                if self.vel.y < 0:
                    if hits[0].state == "moveable":
                        print("i hit a moveable block...")
                        hits[0].vel.y += self.vel.y
                        if len(hits) > 1:
                            if hits[1].state == "unmovable":
                                self.pos.y = hits[1].rect.bottom
                    else:
                        self.pos.y = hits[0].rect.bottom
                self.vel.y = 0
                # hits[0].vel.x = 0
                self.rect.y = self.pos.y
    
    def collide_with_stuff(self, group, kill):
        hits = pg.sprite.spritecollide(self, group, kill)
        if hits: 
            if str(hits[0].__class__.__name__) == "Mob":
                if self.cd.ready():
                    self.health -= 10
                    self.cd.start()
                # print("Ouch!")
            if str(hits[0].__class__.__name__) == "Coin":
                self.coins += 1
                print(self.coins)

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
        # print(self.cd.ready())
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
# Adds 
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
        # self.rect.x = x * TILESIZE[0]
        # self.rect.y = y * TILESIZE[1]
        self.speed = 5
        print(self.pos)
    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
            if hits:
                # print(self.pos)
                if self.vel.x > 0:
                    self.pos.x = hits[0].rect.left - self.rect.width
                if self.vel.x < 0:
                    self.pos.x = hits[0].rect.right
                self.rect.x = self.pos.x
                self.vel.x *= choice([-1,1])
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
            if hits:
                if self.vel.y > 0:
                    self.pos.y = hits[0].rect.top - self.rect.height
                if self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom
                self.rect.y = self.pos.y
                self.vel.y *= choice([-1,1])
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
class Wall(Sprite):
    def __init__(self, game, x, y, state):
        self.groups = game.all_sprites, game.all_walls
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface(TILESIZE)
        self.image.fill(GREY)
        self.rect = self.image.get_rect()
        self.vel = vec(0,0)
        self.pos = vec(x,y) * TILESIZE[0]
        self.state = state
        # print("wall created at", str(self.rect.x), str(self.rect.y))
    
    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
            if hits:
                
                # print(self.pos)
                if self.vel.x > 0:
                    print("a wall collided with a wall")
                    if hits[0].state == "moveable":
                        print("i hit a moveable block...")
                        hits[0].pos.x += self.vel.x
                        if len(hits) > 1:
                            if hits[1].state == "unmoveable":
                                self.pos.x = hits[1].rect.left - self.rect.width
                    else:
                        self.pos.x = hits[0].rect.left - self.rect.width
                        
                if self.vel.x < 0:
                    if hits[0].state == "moveable":
                        print("i hit a moveable block...")
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
                # print(self.pos)
                
                if self.vel.y > 0:
                    print('wall y collide down')
                    if hits[0].state == "moveable":
                        print("i hit a moveable block...")
                        hits[0].pos.y += self.vel.y
                        if len(hits) > 1:
                            if hits[1].state == "unmoveable":
                                self.pos.y = hits[1].rect.top - self.rect.height
                    else:
                        self.pos.y = hits[0].rect.top - self.rect.height
                        
                if self.vel.y < 0:
                    if hits[0].state == "moveable":
                        print("i hit a moveable block...")
                        hits[0].pos.y += self.vel.y
                        if len(hits) > 1:
                            if hits[1].state == "unmovable":
                                self.pos.y = hits[1].rect.bottom
                    else:
                        self.pos.y = hits[0].rect.bottom
                self.vel.y = 0
                self.rect.y = self.pos.y
    def update(self):
        # wall
        self.pos += self.vel
        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        self.rect.y = self.pos.y
        self.collide_with_walls('y')

class MoveableBall(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_moveable_balls
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.ball_img
        self.image.set_colorkey(BLACK)
        #self.image = pg.Surface((TILESIZE[0], TILESIZE[1]), pg.SRCALPHA)
        #pg.draw.circle(self.image, (0, 200, 255), (TILESIZE[0] // 2, TILESIZE[1] // 2), TILESIZE[0] // 2)
        self.rect = self.image.get_rect()
        self.pos = vec(x, y) * TILESIZE[0]
        self.rect.topleft = self.pos
        self.vel = vec(randint(-3, 3), randint(-3, 3))
        self.state = "moveable"
        # gradual slowdown
        self.friction = 0.98
        # reverses direction on bounce
        self.bounce = -1     
        # could expand to affect collision strength
        self.mass = 1         

    # If the ball's left or right side overlaps the edge of the screen's width and height,
    # then the ball bounces back by changing the vector in the opposite direction
    def collide_with_edges(self):
        """Bounce off screen edges."""
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.vel.x *= self.bounce
            self.rect.x = max(0, min(self.rect.x, WIDTH - self.rect.width))
            self.pos.x = self.rect.x

        if self.rect.top < 0 or self.rect.bottom > HEIGHT:
            self.vel.y *= self.bounce
            self.rect.y = max(0, min(self.rect.y, HEIGHT - self.rect.height))
            self.pos.y = self.rect.y

    def collide_with_walls(self):
        """Bounce off unmoveable walls."""
        hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
        for hit in hits:
            if hit == self:
                continue
            if hit.state == "unmoveable":
                if abs(self.rect.right - hit.rect.left) < 10 and self.vel.x > 0:
                    self.rect.right = hit.rect.left
                    self.vel.x *= self.bounce
                elif abs(self.rect.left - hit.rect.right) < 10 and self.vel.x < 0:
                    self.rect.left = hit.rect.right
                    self.vel.x *= self.bounce
                elif abs(self.rect.bottom - hit.rect.top) < 10 and self.vel.y > 0:
                    self.rect.bottom = hit.rect.top
                    self.vel.y *= self.bounce
                elif abs(self.rect.top - hit.rect.bottom) < 10 and self.vel.y < 0:
                    self.rect.top = hit.rect.bottom
                    self.vel.y *= self.bounce
                self.pos = vec(self.rect.topleft)

    # initializes the player
    # measures the dfference between the player and the ball
    def collide_with_player(self):
        """Bounce off the player."""
        player = self.game.player
        if self.rect.colliderect(player.rect):
            # direction from player to ball
            diff = self.pos - player.pos
            if diff.length() == 0:
                diff = vec(1, 0)
            diff = diff.normalize()

            # push ball away from player
            impact_strength = player.vel.length() + 5  # stronger if player is moving fast
            self.vel += diff * impact_strength

            # optionally push the player slightly back
            player.pos -= diff * 5
            player.rect.topleft = player.pos

    def update(self):
        self.pos += self.vel
        self.rect.topleft = self.pos

        self.collide_with_edges()
        self.collide_with_walls()
        self.collide_with_player()

        # Apply friction
        self.vel *= self.friction
        if self.vel.length() < 0.1:
            self.vel = vec(0, 0)


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
        print
    def update(self):
        self.pos += self.vel * self.speed
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        hits = pg.sprite.spritecollide(self, self.game.all_walls, True)
        if hits:
            self.kill()
        
