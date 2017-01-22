#!/usr/bin/env python3
#--------------------------------
#imports
#--------------------------------

import pygame
import math
import os
import random
from sys import argv,exit

import settings
import intro
from generate_world import *
#--------------------------------
#settings variables
#--------------------------------

class Controls():

    def update_relative_controls(self):
        self.direction += self.k_right - self.k_left
        self.acceleration += self.k_up - self.k_down
        
    def update_absolute_controls(self):
        in_x, in_y =  self.k_right - self.k_left, self.k_up - self.k_down
        #print("in: (" + str(in_x) + ", " + str(in_y) + ")")
        accel_percentage = self.acceleration / settings.MAX_ACCELERATION
        cur_x, cur_y = self._get_changes()
        diff_x = cur_x + in_x
        diff_y = cur_y + in_y
        
        #    Input interpretation
        #        +1 (y)
        # (x) -1    +1 (x)
        #        -1 (y)

        #  Direction interpretation (deg)
        #       180
        #    90     270
        #        0

        if in_x == 0 and in_y == 0:
            in_dir = self.direction
        elif in_x == 0 and in_y > 0:
            in_dir = 180
        elif in_x == 0 and in_y < 0:
            in_dir = 0
        elif in_x < 0 and in_y == 0:
            in_dir = 270
        elif in_x > 0 and in_y == 0:
            in_dir = 90
                
        else:
            in_dir = 180 / math.pi * math.acos(-in_y/math.sqrt(in_x*in_x + in_y * in_y))
            if in_x < 0:
                in_dir *= -1

            #              ^
            #              |  cos(a) = in . (-e_y) / (||in|| ||-e_y||)
            #              |         = -in_y  / sqrt(in_x^2 + in_y^2)
            #              |
            #              |
            #     ---------+---------->
            #            /a| |
            #           /  | | -y_in
            #          /___| |
            #              |
            #        -x_in 

        dif_dir = (self.direction - in_dir) % 360
        #print("dif dir: " + str(dif_dir))
        if dif_dir >= (360 - settings.TURN_RATE) or dif_dir <= (settings.TURN_RATE):
            self.direction = in_dir
        else:
            if dif_dir < 180:
                self.direction -= settings.TURN_RATE
            else:
                self.direction += settings.TURN_RATE
                
        if self.spacebar > 0:
            self.acceleration = max(-1, self.acceleration - 0.3)
        else:
            euclidean_norm = math.sqrt( diff_x * diff_x + diff_y * diff_y) # \in [0,2]
            #print("norm: " + str(euclidean_norm))
            self.acceleration += abs(euclidean_norm - 1)

        #print("acceleration: " + str(self.acceleration))

    def get_direction(self):
        return self.direction

    def get_changes(self):
        return self._get_changes()

    def _get_changes(self):
        rad = self.direction * math.pi / 180
        x = math.sin(rad)
        y = math.cos(rad)
        return x,y
    def get_acceleration(self):
        return self.acceleration
    def get_speed(self):
        return self.speed

    def __init__(self):
        self.k_left = 0
        self.k_right = 0 
        self.k_down = 0 
        self.k_up = 0
        self.spacebar = 0
        self.acceleration = 0
        self.direction = 90
        self.speed = 0
        #TODO: something like self.update_fun = update_relative_controls

    def update(self):
        self.direction = self.direction % 360
        if abs(self.acceleration) > settings.MAX_ACCELERATION:
            self.acceleration = self.acceleration / abs(self.acceleration) * settings.MAX_ACCELERATION
        #self.update_relative_controls()
        self.update_absolute_controls()
        self.speed += self.acceleration * 0.5
        if self.speed > settings.MAX_FORWARD_SPEED:
            self.speed = settings.MAX_FORWARD_SPEED
        if self.speed < settings.MAX_REVERSE_SPEED:
            self.speed = settings.MAX_REVERSE_SPEED
#--------------------------------
# sprite classes
#--------------------------------

class KorandoSprite(pygame.sprite.Sprite):
    MAX_DAMAGE = 3
    TURN_SPEED = 5

    def __init__(self, image, position):


        pygame.sprite.Sprite.__init__(self)
        self.src_images = []
        for img in [settings.KORANDO, settings.KORANDO_SMOKE, settings.KORANDO_FIRE, settings.KORANDO_EXPLOSION]: 
            self.src_images.append(pygame.image.load(img))
        self.image = self.src_images[0]
        self.position = position
        self.moving = True 
        self.speed = 0 
        self.acceleration = 0 
        self.direction = 0
        self.k_left = 0
        self.k_right = 0 
        self.k_down = 0 
        self.k_up = 0
        self.damage = 0
        self.last_coll = []
        self.rect = pygame.Rect(self.src_images[0].get_rect())
        self.rect.center = position
    def update(self, game, deltat):
        # SIMULATION
        #print("speed : " + str(self.speed) + ", up: " + str(self.k_up) + ", down:  " + str(self.k_down) )

        tree_collisions = pygame.sprite.groupcollide(game.tree_group, game.korando_group, 0, 0)
        street_collisions = pygame.sprite.groupcollide(game.street_group, game.korando_group, 0, 0)
        sidewalk_collisions = pygame.sprite.groupcollide(game.sidewalk_group, game.korando_group, 0, 0)
        #print("collisions: " + str(collisions))
        for colider in tree_collisions:
          if self in tree_collisions[colider] and colider not in self.last_coll:
            self.damage += 1
            self.last_coll.append(colider)
            if self.damage >= self.MAX_DAMAGE:
                self.damage = self.MAX_DAMAGE
                self.image = pygame.transform.rotate(self.src_images[self.damage], self.direction)
        if self.damage >= self.MAX_DAMAGE:
            self.moving = False

        speed_factor = 1
        if street_collisions == {}: #not on the street
            speed_factor *= 0.6
            if sidewalk_collisions == {}: #neither on the sidewalk
              speed_factor *= 0.6

        if self.moving == True: 
            #print("damage: " + str(self.damage))
            game.controls.update()
            self.acceleration = game.controls.get_acceleration() 
            self.speed = game.controls.get_speed() * speed_factor
            self.direction = game.controls.get_direction()
            x, y = self.position
            dx, dy = game.controls.get_changes()
            #print("changes: (" + str(dx) + ", " + str(dy))
            x += self.speed * dx
            y += self.speed * dy
            if x < 0:
                x = 0
            if x > game.level_width:
                x = game.level_width
            if y < 0:
                y = 0
            if y > game.level_height:
                y = game.level_height
            self.position = (x, y)
            self.image = pygame.transform.rotate(self.src_images[self.damage], self.direction)
            self.rect = self.image.get_rect()
            self.rect.center = self.position
        #print("direction: " + str(self.direction)

class TreeSprite(pygame.sprite.Sprite):
    normal = pygame.image.load(settings.TREE)
    hit = pygame.image.load(settings.TREE_EXPLOSION)
    was_hit = False
    def __init__(self, position):
        self.rect = pygame.Rect(self.normal.get_rect())
        self.rect.center = position
        self.image = self.normal
        pygame.sprite.Sprite.__init__(self)
    def update(self, game):
        #print(str(hit_list))
        hit_list = pygame.sprite.groupcollide(game.tree_group, game.korando_group, 0, 0)
        #print("collisions: " + str(collisions))
        if self in hit_list:
           self.was_hit = True
        if self.was_hit:
           self.image = self.hit
        else: self.image = self.normal

class GoalSprite(pygame.sprite.Sprite):
    def __init__(self, position):
        self.image = pygame.image.load(settings.GOAL)
        self.rect = pygame.Rect(self.image.get_rect())
        self.rect.center = position
        pygame.sprite.Sprite.__init__(self)

class StreetSprite(pygame.sprite.Sprite):
    def __init__(self, position):
        self.image = pygame.image.load(settings.STREET)
        self.rect = pygame.Rect(self.image.get_rect())
        self.rect.center = position
        pygame.sprite.Sprite.__init__(self)

class SidewalkSprite(pygame.sprite.Sprite):
    def __init__(self, position):
        self.image = pygame.image.load(settings.SIDEWALK)
        self.rect = pygame.Rect(self.image.get_rect())
        self.rect.center = position
        pygame.sprite.Sprite.__init__(self)

#--------------------------------
# other game classes
#--------------------------------
class GameInstance:
    def __init__(self,screen):
        self.controls = Controls()
        self.world = World()
        self.world.generate_stepwise()
        self.level_height = self.world.WORLD_HEIGHT * 100
        self.level_width = self.world.WORLD_WIDTH * 100
        self.entities = pygame.sprite.Group()
        self.tree_group = pygame.sprite.Group()
        self.street_group = pygame.sprite.Group()
        self.goal_group = pygame.sprite.Group()
        self.sidewalk_group = pygame.sprite.Group()
        for j in range(self.world.WORLD_HEIGHT):
            for i in range(self.world.WORLD_WIDTH):
                x = i * 100
                y = j * 100
                if  self.world.p(i,j) == 'T':
                    tree = TreeSprite((x,y))
                    self.entities.add(tree)
                    self.tree_group.add(tree)
                elif self.world.p(i,j) == '=':
                    street = StreetSprite((x,y))
                    self.entities.add(street)
                    self.street_group.add(street)
                elif self.world.p(i,j) == 'G':
                    street = GoalSprite((x,y))
                    self.entities.add(street)
                    self.street_group.add(street)
                    self.goal_group.add(street)
                elif self.world.p(i,j) == 'S':
                    sidewalk = SidewalkSprite((x,y))
                    self.entities.add(sidewalk)
                    self.sidewalk_group.add(sidewalk)

                              
        i,j = self.world.init_pos
        x = i * 100
        y = j * 100
        self.korando = KorandoSprite(settings.KORANDO, (x,y))
        self.korando_group = pygame.sprite.RenderPlain(self.korando)
        self.entities.add(self.korando)
        
        
        #self.tree_group = pygame.sprite.RenderPlain(*self.trees)
         
    
    def clear_game(self,screen,background):
        for e in self.entities:
            e.kill()
        screen.blit(background, (0,0))

#from: http://stackoverflow.com/questions/14354171/add-scrolling-to-a-platformer-in-pygame 
class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = pygame.Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)

def simple_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    return Rect(-l+settings.HALF_WIDTH, -t+settings.HALF_HEIGHT, w, h)

def complex_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t, _, _ = -l+settings.HALF_WIDTH, -t+settings.HALF_HEIGHT, w, h

    l = min(0, l)                           # stop scrolling at the left edge
    l = max(-(camera.width-settings.WIN_WIDTH), l)   # stop scrolling at the right edge
    t = max(-(camera.height-settings.WIN_HEIGHT), t) # stop scrolling at the bottom
    t = min(0, t)                           # stop scrolling at the top
    return pygame.Rect(l, t, w, h)

#--------------------------------
# main loop
#--------------------------------
def main():
    intro.main()
    clock = pygame.time.Clock()
    deltat = clock.tick(settings.FRAMES_PER_SECOND)
    
    #for testing:
    screen = pygame.display.set_mode(settings.DISPLAY, settings.VIDEO_FLAGS, settings.DEPTH)
        
    pygame.display.set_caption(settings.TITLE_STRING)
    background = pygame.image.load(settings.BACKGROUND)
    screen.blit(background, (0,0))
    rect = screen.get_rect()
    
    game = GameInstance(screen)
    restart = False
    camera = Camera(complex_camera, game.level_width, game.level_height)
    
    while 1:
        # user input
        deltat = clock.tick(30)
        for event in pygame.event.get():
            if not hasattr(event, 'key'): continue
            down = event.type == pygame.KEYDOWN
            if event.key == pygame.K_RIGHT: game.controls.k_right = down 
            elif event.key == pygame.K_LEFT: game.controls.k_left = down
            elif event.key == pygame.K_UP: game.controls.k_up = down 
            elif event.key == pygame.K_DOWN: game.controls.k_down = down
            elif event.key == pygame.K_SPACE: game.controls.spacebar = down
            elif event.key == pygame.K_DELETE: exit(0)
            elif event.key == pygame.K_r and event.type == pygame.KEYUP: restart = True
    
        # rendering
        screen.blit(background, (0,0)) #is this too inefficient?
        camera.update(game.korando)
        for e in game.entities:
            screen.blit(e.image, camera.apply(e))

        # hack: get korando always on top (should get a good method to decide this for more complex interactions)
        screen.blit(game.korando.image, camera.apply(game.korando)) 
    
        if restart == True:
            game.clear_game(screen,background)
            del game
            game = GameInstance(screen)
            del camera
            camera = Camera(complex_camera, game.level_width, game.level_height)
            restart = False
    
        game.tree_group.update(game)
        game.korando_group.update(game,deltat)
    
        pygame.display.flip()

if __name__ == "__main__":
    main()
