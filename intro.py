#!/usr/bin/env python3


import pygame, os
from math import sin

import settings

def main():
    #initialize and setup screen
    pygame.init()
    screen = pygame.display.set_mode(settings.DISPLAY, pygame.HWSURFACE|pygame.DOUBLEBUF)

    #load images and scale
    drakoon_image = pygame.image.load(settings.WELCOME_SCREEN)
    drakoon_image = pygame.transform.scale(drakoon_image,settings.DISPLAY)
    racing_image = pygame.image.load(settings.RACING_IMG)
    #drakoon_image = pygame.transform.scale(racing_image,settings.DISPLAY) #TODO: make general for different resolutions

    #get the image and screen in the same format
    if screen.get_bitsize() == 8:
        screen.set_palette(drakoon_image.get_palette())
    else:
        drakoon_image = drakoon_image.convert()

    #prep some variables
    anim = 0.0
    racing_pos = settings.RACING_END_POSITION_OFFSET
    racing_pos = (0, racing_pos[1])
    racing_accel = 0.085
    racing_speed = 0
    clock = pygame.time.Clock()
    deltat = clock.tick(settings.FRAMES_PER_SECOND)
    reached = False


    #mainloop
    xblocks = range(0, settings.WIN_WIDTH, 20)
    yblocks = range(0, settings.WIN_HEIGHT , 20)
    stopevents = pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN
    while 1:
        for e in pygame.event.get():
            if e.type in stopevents:
                return

        deltat = clock.tick(30)
        screen.blit(drakoon_image, (0, 0))
        if racing_pos[0] < settings.RACING_END_POSITION_OFFSET[0] and reached == False: 
            racing_accel = 0.00045
        elif racing_pos[0] > settings.RACING_END_POSITION_OFFSET[0]:
            racing_accel = -0.0015
            reached = True
        else:
            racing_accel = 0
            racing_speed = 0
            racing_pos = settings.RACING_END_POSITION_OFFSET

        racing_speed += racing_accel * deltat
        racing_pos = (racing_pos[0] + int(racing_speed * deltat), racing_pos[1])
        #print(" racing pos: " + str(racing_pos))
        screen.blit(racing_image, racing_pos)

            
        

        pygame.display.flip()

if __name__ == '__main__': main()


