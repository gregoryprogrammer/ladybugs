import sys
import random

# Dane do połączenia
HOST = 'localhost'
PORT = 32323

# Identyfikator biedronki
BUG_ID = 'R1'

# Nazwa biedronki
BUG_NAME = 'Bez nazwy'

try:
    HOST = sys.argv[1]
    BUG_ID = sys.argv[2]
    BUG_NAME = sys.argv[3]
except:
    pass

def losowy_ruch(dane):
    rozkaz = random.choice(['N', 'S', 'W', 'E'])
    return rozkaz

def na_wschod(dane):
    return 'E'

PROGRAM = losowy_ruch
