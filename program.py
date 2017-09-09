import sys
import random

import pygame

# Dane do połączenia
HOST = 'localhost'
PORT = 32323

# Identyfikator biedronki
BUG_ID = 'XXXX'

# Nazwa biedronki
BUG_NAME = 'NAZWA ROBAKA'

def losowy_ruch(dane):
    rozkaz = random.choice(['N', 'S', 'W', 'E'])
    return rozkaz

def na_wschod(dane):
    return 'E'

def dookola(dane):
    pole_E = dane.get('E')
    pole_S = dane.get('S')
    pole_W = dane.get('W')
    pole_N = dane.get('N')

    if pole_N == '#' and pole_E != '#':
        rozkaz = 'E'
    elif pole_E == '#' and pole_S != '#':
        rozkaz = 'S'
    elif pole_S == '#' and pole_W != '#':
        rozkaz = 'W'
    elif pole_W == '#' and pole_N != '#':
        rozkaz = 'N'

    return rozkaz

def do_pierwszego(dane):
    pozycja_biedronki = dane.get('position')
    cukierki = dane.get('sweets')

    if len(cukierki) == 0:
        return 'X'

    pierwszy_cukierek = cukierki[0]

    bx, by = pozycja_biedronki
    cx, cy = pierwszy_cukierek

    if bx > cx:
        return 'W'
    elif bx < cx:
        return 'E'
    elif by > cy:
        return 'N'
    else:
        return 'S'

def sterowanie_klawiszami(dane):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] == True:
        return 'W'
    elif keys[pygame.K_RIGHT] == True:
        return 'E'
    elif keys[pygame.K_UP] == True:
        return 'N'
    elif keys[pygame.K_DOWN] == True:
        return 'S'
    return 'X'


PROGRAM = sterowanie_klawiszami
# PROGRAM = losowy_ruch
# PROGRAM = na_wschod
# PROGRAM = dookola
# PROGRAM = do_pierwszego
