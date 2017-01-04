#!/usr/bin/python3

#--------------------------------
#imports
#--------------------------------

import pygame
import math
import os
import random
from sys import argv,exit

#--------------------------------
#settings variables
#--------------------------------

#constants
WIN_WIDTH = 1024
WIN_HEIGHT = 768
HALF_WIDTH = int(WIN_WIDTH / 2)
HALF_HEIGHT = int(WIN_HEIGHT / 2)

DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
DEPTH = 32
VIDEO_FLAGS = 0
FRAMES_PER_SECOND = 30
CAMERA_SLACK = 30

#other variables
RACINGGAME_ROOT = os.path.realpath(argv[0]).split('/')
RACINGGAME_ROOT.pop(-1)
RACINGGAME_ROOT = "/".join(RACINGGAME_ROOT)
FIGS = RACINGGAME_ROOT + "/figs/"

KORANDO = FIGS + "korando.png"
KORANDO_FIRE = FIGS + "korando_fire.png"
KORANDO_SMOKE = FIGS + "korando_smoke.png"
KORANDO_EXPLOSION = FIGS + "korando_explosion.png"

TREE = FIGS + "tree.png"
TREE_EXPLOSION = FIGS + "tree_explosion.png"

BACKGROUND = FIGS + 'background.png'
#--------------------------------
# setup
#--------------------------------
clock = pygame.time.Clock()
deltat = clock.tick(FRAMES_PER_SECOND)

#for testing:
screen = pygame.display.set_mode(DISPLAY, VIDEO_FLAGS, DEPTH)

#for gameplay
#screen = pygame.display.set_mode((1024,768),FULLSCREEN, DOUBLEBUFF)
#pygame.display.flip()

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
        for img in [KORANDO, KORANDO_SMOKE, KORANDO_FIRE, KORANDO_EXPLOSION]: 
            self.src_images.append(pygame.image.load(img))
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
    def update(self, deltat,collisions):
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
            y += self.speed * math.cos(rad)
            self.position = (x, y)
            self.image = pygame.transform.rotate(self.src_images[self.damage], self.direction)
            self.rect = self.image.get_rect()
            self.rect.center = self.position

class TreeSprite(pygame.sprite.Sprite):
    normal = pygame.image.load(TREE)
    hit = pygame.image.load(TREE_EXPLOSION)
    was_hit = False
    def __init__(self, position):
        self.rect = pygame.Rect(self.normal.get_rect())
        self.rect.center = position
        pygame.sprite.Sprite.__init__(self)
    def update(self, hit_list):
        #print(str(hit_list))
        if self in hit_list:
           self.was_hit = True
        if self.was_hit:
           self.image = self.hit
        else: self.image = self.normal

class GameInstance:
    def __init__(self):
        self.korando = KorandoSprite(FIGS + 'korando.png', rect.center)
        self.korando_group = pygame.sprite.RenderPlain(self.korando)
        
        num_trees = random.randint(3,11)
        self.trees = []
        for i in range(num_trees):
            x,y = random.randint(0,1024), random.randint(0,768)
            self.trees.append(TreeSprite((x,y)))
        
        self.tree_group = pygame.sprite.RenderPlain(*self.trees)
        pygame.display.flip()
         
    
    def clear_game(self):
        try:
           self.korando.kill()
        except:
           self.korando = None
        try:
            for tree in self.trees:
                tree.kill()
            self.trees = []
        except:
            self.trees = []
        screen.blit(background, (0,0))
    
#--------------------------------
# game loop
#--------------------------------
background = pygame.image.load(BACKGROUND)
screen.blit(background, (0,0))
rect = screen.get_rect()

game = GameInstance()
restart = False

while 1:
    # USER INPUT
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
    # RENDERING
    game.tree_group.clear(screen, background)
    game.korando_group.clear(screen, background)

    if restart == True:
        game.clear_game()
        del game
        game = GameInstance()
        restart = False

    collisions = pygame.sprite.groupcollide(game.tree_group, game.korando_group, 0, 0)
    #print("collisions: " + str(collisions))
    game.tree_group.update(collisions)
    game.korando_group.update(deltat,collisions)
    game.korando_group.update(deltat,collisions)

    game.tree_group.draw(screen)
    game.korando_group.draw(screen)
    pygame.display.flip()
