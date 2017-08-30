import sys
import random

# Dane do połączenia
HOST = 'localhost'
PORT = 32323

# Identyfikator biedronki
BUG_ID = 'R1'

# Nazwa biedronki
BUG_NAME = 'Bez nazwy'

def losowy_ruch(dane):
    rozkaz = random.choice(['N', 'S', 'W', 'E'])
    return rozkaz

def na_wschod(dane):
    return 'E'

PROGRAM = losowy_ruch
