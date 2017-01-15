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

#--------------------------------
# sprite classes
#--------------------------------

class KorandoSprite(pygame.sprite.Sprite):
    MAX_FORWARD_SPEED = 8
    MAX_REVERSE_SPEED = -3
    MAX_DAMAGE = 3
    TURN_SPEED = 5

    def __init__(self, image, position):


        pygame.sprite.Sprite.__init__(self)
        self.src_images = []
        for img in [settings.KORANDO, settings.KORANDO_SMOKE, settings.KORANDO_FIRE, settings.KORANDO_EXPLOSION]: 
            self.src_images.append(pygame.image.load(img))
        self.image = self.src_images[0]
        self.position = position
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
    def update(self, game, deltat,collisions):
        # SIMULATION
        #print("speed : " + str(self.speed) + ", up: " + str(self.k_up) + ", down:  " + str(self.k_down) )
        for colider in collisions:
          if self in collisions[colider] and colider not in self.last_coll:
            self.damage += 1
            self.last_coll.append(colider)
            if self.damage >= self.MAX_DAMAGE:
                self.damage = self.MAX_DAMAGE
                self.image = pygame.transform.rotate(self.src_images[self.damage], self.direction)

        if self.damage < self.MAX_DAMAGE:
            #print("damage: " + str(self.damage))
            self.acceleration = (self.k_up - self.k_down)
            self.speed += self.acceleration * 0.5
            if self.speed > self.MAX_FORWARD_SPEED:
                self.speed = self.MAX_FORWARD_SPEED
            if self.speed < self.MAX_REVERSE_SPEED:
                self.speed = self.MAX_REVERSE_SPEED
            self.direction += (self.k_right - self.k_left)
            x, y = self.position
            rad = self.direction * math.pi / 180
            x += self.speed * math.sin(rad)
            if x < 0:
                x = 0
            if x > game.level_width:
                x = game.level_width
            y += self.speed * math.cos(rad)
            if y < 0:
                y = 0
            if y > game.level_height:
                y = game.level_height
            self.position = (x, y)
            self.image = pygame.transform.rotate(self.src_images[self.damage], self.direction)
            self.rect = self.image.get_rect()
            self.rect.center = self.position

class TreeSprite(pygame.sprite.Sprite):
    normal = pygame.image.load(settings.TREE)
    hit = pygame.image.load(settings.TREE_EXPLOSION)
    was_hit = False
    def __init__(self, position):
        self.rect = pygame.Rect(self.normal.get_rect())
        self.rect.center = position
        self.image = self.normal
        pygame.sprite.Sprite.__init__(self)
    def update(self, hit_list):
        #print(str(hit_list))
        if self in hit_list:
           self.was_hit = True
        if self.was_hit:
           self.image = self.hit
        else: self.image = self.normal

#--------------------------------
# other game classes
#--------------------------------
class GameInstance:
    def __init__(self,screen):
        self.korando = KorandoSprite(settings.KORANDO, screen.get_rect().center)
        self.korando_group = pygame.sprite.RenderPlain(self.korando)
        
        self.level_height = random.randint(settings.WIN_HEIGHT,settings.MAX_WORLD_SIZE_MULTIPLIER * settings.WIN_HEIGHT)
        self.level_width = random.randint(settings.WIN_WIDTH,settings.MAX_WORLD_SIZE_MULTIPLIER * settings.WIN_WIDTH)
        self.num_trees = random.randint(3,11) * int(self.level_width/settings.WIN_WIDTH)* int(self.level_height/settings.WIN_HEIGHT)
        self.entities = pygame.sprite.Group()
        self.tree_group = pygame.sprite.Group()
        self.entities.add(self.korando)
        for i in range(self.num_trees):
            x,y = random.randint(0,self.level_height), random.randint(0,self.level_width)
            tree = TreeSprite((x,y))
            self.entities.add(tree)
            self.tree_group.add(tree)
        
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
            if event.key == pygame.K_RIGHT: game.korando.k_right = down * 5
            elif event.key == pygame.K_LEFT: game.korando.k_left = down * 5
            elif event.key == pygame.K_UP: game.korando.k_up = down * 2
            elif event.key == pygame.K_DOWN: game.korando.k_down = down * 2
            elif event.key == pygame.K_DELETE: exit(0)
            elif event.key == pygame.K_r and event.type == pygame.KEYUP: restart = True
    
        # rendering
        screen.blit(background, (0,0))
        camera.update(game.korando)
        for e in game.entities:
            screen.blit(e.image, camera.apply(e))
    
        if restart == True:
            game.clear_game(screen,background)
            del game
            game = GameInstance(screen)
            del camera
            camera = Camera(complex_camera, game.level_width, game.level_height)
            restart = False
    
        collisions = pygame.sprite.groupcollide(game.tree_group, game.korando_group, 0, 0)
        #print("collisions: " + str(collisions))
        game.tree_group.update(collisions)
        game.korando_group.update(game,deltat,collisions)
        game.korando_group.update(game,deltat,collisions)
    
        pygame.display.flip()

if __name__ == "__main__":
    main()
