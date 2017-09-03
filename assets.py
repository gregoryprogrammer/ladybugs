import os
import sys
import pygame

MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]

def load_image(filename):
    filepath = os.path.join(MAIN_DIR, 'assets', filename)
    try:
        surface = pygame.image.load(filepath)
    except:
        print(filepath, sys.exc_info())
        exit(1)
    return surface

def load_font(filename, size):
    filepath = os.path.join(MAIN_DIR, 'assets', filename)
    font = pygame.font.Font(filepath, size)
    return font

def create_highlight(tile, color):
    surface = pygame.Surface((tile, tile))
    surface.fill((color))
    surface.set_alpha(20)
    return surface

LADYBUGS_DIR = os.path.join(MAIN_DIR, 'assets', 'ladybugs')
LADYBUGS_IMAGES = [ x for x in os.listdir(LADYBUGS_DIR) if x.endswith('png')]
LADYBUGS_IDS = [os.path.splitext(bug)[0] for bug in LADYBUGS_IMAGES]
LADYBUGS_SURFACES = [load_image(os.path.join(LADYBUGS_DIR, bug)) for bug in LADYBUGS_IMAGES]

LADYBUGS = dict(zip(LADYBUGS_IDS, LADYBUGS_SURFACES))

def get_bug_img(bug_id):
    bug_img = LADYBUGS.get(bug_id)
    return bug_img
