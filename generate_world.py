import pygame
import random
import numpy.random


class World():
    WORLD_WIDTH = 120
    WORLD_HEIGHT = 25
    
    PROB_STEP = 0.025
    PROB_CONTINUE = 0.8
    PROB_CHANGE = 0.2

    TOTAL_TREE_ATTEMPTS = 100
    
    world_items = ['=', #street
                   'S', #sidewalk
                   'B', #building
                   '~', #grass
                   'T', #tree
                   '`'] #nothing (background)

    def __init__(self):
        self.world = dict()
        self.init_pos = (0,0)
    
    def generate_full_random():
        for j in range(self.WORLD_HEIGHT):
            for i in range(self.WORLD_WIDTH):
                cur_type = random.randint(1,len(world_items)) - 1
                self.world[(i,j)] = world_items[cur_type]
        self.init_pos = (random.randint(0,self.WORLD_WIDTH-1), random.randint(0,self.WORLD_HEIGHT-1))
    
    def generate_stepwise(self):
    
        ###################################
        #first step: streets and sidewalks.
        ###################################
        # A street has to have a sidewalk.
        # Thus, they cannot start and end at the borders
        # Streets also need to be connected, so we will
        # iterate from left to right over all columns
        # and add streets either exactly at the same height
        # or diagonal. The chances of what happens will 
        # increase gradually the longer it has not happened.
        p_continue = self.PROB_CONTINUE
        p_change = self.PROB_CHANGE
    
        assert( int(p_continue / self.PROB_STEP) - (p_continue / self.PROB_STEP) == 0)
        assert( int(p_change / self.PROB_STEP) - (p_change / self.PROB_STEP) == 0)
        assert( p_continue + p_change == 1)
    
        #extra space (2) to avoid special cases at start 
        last_pos = random.randint(2,self.WORLD_HEIGHT-2) 
        step_diff = 0
        self.init_pos = (0,last_pos)
    
        for i in range(self.WORLD_WIDTH): 
    
            if last_pos == self.WORLD_HEIGHT - 1: #special case: go down now!
                p_continue = self.PROB_CONTINUE
                p_change = self.PROB_CHANGE
                assert( p_continue + p_change == 1)
                step_diff = -1
                
            elif last_pos == 1: #special case: go up now!
                p_continue = self.PROB_CONTINUE
                p_change = self.PROB_CHANGE
                assert( p_continue + p_change == 1)
                step_diff = 1
    
            else: #normal case: choose via probabilities
                action = numpy.random.choice( ['cont','change'], 1, p=[p_continue,p_change])
                if(action == 'cont'):
                    p_continue -= self.PROB_STEP
                    p_change +=  self.PROB_STEP
                    assert( p_continue + p_change == 1)
                else:
                    #change. 
                    l = [0,1,-1]
                    l.remove(step_diff)
                    step_diff = random.choice(l)
                    p_continue = self.PROB_CONTINUE
                    p_change =  self.PROB_CHANGE
                    assert( p_continue + p_change == 1)
    
            #actually update position and add sidewalk
            j = last_pos + step_diff
            last_pos = j
            self.world[(i,j)] = '='
            self.world[(i,j-1)] = 'S'
            self.world[(i,j+1)] = 'S'
        
        
        ##################################################
        #tree step: add spread-out trees in the background 
        ##################################################
        for _ in range(self.TOTAL_TREE_ATTEMPTS):
            i = random.randint(0,self.WORLD_WIDTH-1)
            j = random.randint(0,self.WORLD_HEIGHT-1)
            if (i,j) in self.world:
                continue
            else:
                self.world[(i,j)] = 'T'
        ###########################################
        #final step: fill the rest with background.
        ###########################################
        for j in range(self.WORLD_HEIGHT): 
            for i in range(self.WORLD_WIDTH): 
                if (i,j) in self.world:
                    continue
                else:
                    self.world[(i,j)] = '`'
    
        ################
        #final checkups
        ################
        (init_i, init_j) = self.init_pos 
        if self.world[(init_i,init_j)] != '=':
            

            if self.world[(init_i,init_j-1)] == '=':
                self.init_pos = (init_i,init_j-1)
            elif self.world[(init_i,init_j+1)] == '=':
                self.init_pos = (init_i,init_j+1)
            else:
                print("error: no starting position found. this should not happen.")
                print("world[(" + str(init_i) + ", " + str(init_j) + ")]: " + str(self.world[(init_i,init_j)]))
                
    def get_string(self):
        world_string = ""
        for j in range(self.WORLD_HEIGHT): 
            for i in range(self.WORLD_WIDTH): 
                if (i,j) in self.world:
                    world_string += self.world[(i,j)]
                else:
                    world_string += "X"
            world_string += '\n'
        return world_string

        
                

world = World()
world.generate_stepwise()
print(world.get_string())
print("init pos: " + str(world.init_pos))

