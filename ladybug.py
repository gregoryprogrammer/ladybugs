import socket
import sys
import json
import time
import random
import threading

from pprint import pprint

import pygame
import config
import program
import utils
import assets

info = dict()
info['conn_ok'] = False
info['server_msg'] = 'Brak'
info['score'] = 0

BUG_ID = program.BUG_ID
BUG_NAME = program.BUG_NAME
HOST = program.HOST

try:
    HOST = sys.argv[1]
    BUG_ID = sys.argv[2]
    BUG_NAME = sys.argv[3]
except:
    pass


def row(num):
    return num * 32

window = utils.Window(name='Biedronka', size=config.CLIENT_WINDOW_SIZE)

background_img = pygame.Surface(config.CLIENT_WINDOW_SIZE)
background_img.fill(config.COLOR_GRAY)

font = assets.load_font('Ubuntu-Regular.ttf', 24)

conn_ok = font.render('Połączono!', True, config.COLOR_GREEN)
conn_error = font.render('Czekam na połączenie...', True, config.COLOR_RED)

your_txt = font.render('Twoja biedronka: {}'.format(program.BUG_NAME), True, config.COLOR_WHITE)

def client():
    global info

    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(2.0)

            info['conn_ok'] = False
            info['server_msg'] = 'Brak'

            print('Trying to connect...')

            try:
                sock.connect((HOST, program.PORT))
            except ConnectionRefusedError:
                print('Nie moge polaczyc sie do polany! Sprawdz HOST i PORT')
            except:
                print('other except', sys.exc_info())
            else:
                print('Connected!')
                info['conn_ok'] = True

            try:
                sock.sendall(bytes('{},{}'.format(BUG_ID, BUG_NAME), 'utf8'))
                received = str(sock.recv(config.MSG_LEN), 'utf8')
            except:
                print('client greet exc', sys.exc_info())
            else:
                print('Greet received:', received)
                jdata = json.loads(received)
                info['server_msg'] = jdata.get('server_msg')

            try:
                while True:
                    received = sock.recv(config.MSG_LEN)
                    if len(received) == 0:
                        break
                    jdata = json.loads(str(received, 'utf8'))
                    info['score'] = jdata.get('score', 0)
                    info['server_msg'] = jdata.get('server_msg')
                    arena_state = jdata.get('arena_state')

                    order = None
                    if arena_state not in ('challenge_wait', 'pause'):
                        order = program.PROGRAM(jdata)

                    print()
                    utils.printfr('Dane:')
                    pprint(jdata)

                    if order:
                        utils.printfr('Twój rozkaz: ' + order)
                    else:
                        utils.printfr('Brak rozkazu. Przerwa w treningu lub zawodach.')

                    if isinstance(order, str):
                        sock.sendall(bytes(order, 'utf8'))
                    else:
                        sock.sendall(bytes('X', 'utf8'))
            except:
                print(sys.exc_info())
            finally:
                sock.close()

        time.sleep(1.0)

client_thread = threading.Thread(target=client)
client_thread.daemon = True
client_thread.start()

bug_img = assets.get_bug_img(BUG_ID)
info_q_txt = font.render('Wciśnij Q by wyłączyć program.', True, config.COLOR_WHITE)

while window.loop():

    server_txt = font.render('Komunikat serwera: {}'.format(info['server_msg']), True, config.COLOR_WHITE)

    score_txt = font.render('Zebrane cukierki: {}'.format(info['score']), True, config.COLOR_WHITE)
    place_txt = font.render('Miejsce: {}'.format(3), True, (200, 200, 200))

    window.draw(background_img, (0, 0))

    if info['conn_ok']:
        window.draw(conn_ok, (0, row(0)))
    else:
        window.draw(conn_error, (0, row(0)))
    window.draw(info_q_txt, (0, row(1)))
    window.draw(server_txt, (0, row(3)))
    window.draw(your_txt, (0, row(5)))
    window.draw(score_txt, (0, row(6)))
    window.draw(bug_img, (50, row(8)))
    window.render()
