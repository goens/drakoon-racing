#--------------------------------
#settings variables
#--------------------------------
from sys import argv
import os

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

MAX_WORLD_SIZE_MULTIPLIER = 5

TITLE_STRING = " Drakoon Racing!"
RACING_END_POSITION_OFFSET = (470,575)

#other variables
RACINGGAME_ROOT = os.path.split(os.path.abspath(__file__))[0]
FIGS = os.path.join(RACINGGAME_ROOT, "figs", "")

KORANDO = os.path.join(FIGS,"korando.png")
KORANDO_FIRE = os.path.join(FIGS,"korando_fire.png")
KORANDO_SMOKE = os.path.join(FIGS,"korando_smoke.png")
KORANDO_EXPLOSION = os.path.join(FIGS,"korando_explosion.png")
WELCOME_SCREEN = os.path.join(FIGS, 'korando_welcome_screen.png')
RACING_IMG = os.path.join(FIGS, 'racing.png')
TREE = os.path.join(FIGS,"tree.png")
TREE_EXPLOSION = os.path.join(FIGS,"tree_explosion.png")
STREET = os.path.join(FIGS,"street_square.png")
SIDEWALK = os.path.join(FIGS,"sidewalk_square.png")

BACKGROUND = os.path.join(FIGS,'background.png')

TURN_RATE = 4

MAX_FORWARD_SPEED = 8
MAX_REVERSE_SPEED = -3
MAX_ACCELERATION = 5
