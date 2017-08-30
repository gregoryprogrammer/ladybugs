import socket
import sys
import json
import time
import random
import threading

import pygame
import program
import utils
import assets

info = dict()
info['conn_ok'] = False
info['server_msg'] = 'Brak'
info['score'] = 0

def row(num):
    return num * 32

window = utils.Window(name='Biedronka', size=utils.CONF['window'])

background_img = pygame.Surface(utils.CONF['window'])
background_img.fill(utils.COLOR['gray'])

font = assets.load_font('Ubuntu-Regular.ttf', 24)

conn_ok = font.render('Połączono!', True, utils.COLOR['green'])
conn_error = font.render('Czekam na połączenie...', True, utils.COLOR['red'])

your_txt = font.render('Twoja biedronka: {}'.format(program.BUG_NAME), True, utils.COLOR['white'])

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
                sock.connect((program.HOST, program.PORT))
            except ConnectionRefusedError:
                print('Nie moge polaczyc sie do polany! Sprawdz HOST i PORT')
            except:
                print('other except', sys.exc_info())
            else:
                print('Connected!')
                info['conn_ok'] = True

            try:
                sock.sendall(bytes(program.BUG_ID, 'ascii'))
                received = str(sock.recv(utils.MSG_LEN), 'ascii')
            except:
                print('client greet exc', sys.exc_info())
            else:
                print('Greet received:', received)
                jdata = json.loads(received)
                info['server_msg'] = jdata.get('server_msg')

            try:
                while True:
                    print('Waiting for field state')
                    received = sock.recv(utils.MSG_LEN)
                    if len(received) == 0:
                        break
                    jdata = json.loads(str(received, 'ascii'))
                    print('.------------------')
                    print('| Dane:\n| ', end='')
                    print(jdata)

                    info['score'] = jdata.get('score', 0)

                    order = program.PROGRAM(jdata)
                    server_msg = jdata.get('server_msg')
                    print('| Twój rozkaz:', order)
                    print('\'-----')
                    sock.sendall(bytes(order, 'ascii'))
            except:
                print(sys.exc_info())
            finally:
                sock.close()

        time.sleep(1.0)

client_thread = threading.Thread(target=client)
client_thread.daemon = True
client_thread.start()

while window.loop():

    server_txt = font.render('Komunikat serwera: {}'.format(info['server_msg']), True, utils.COLOR['white'])

    score_txt = font.render('Zebrane cukierki: {}'.format(info['score']), True, utils.COLOR['white'])
    place_txt = font.render('Miejsce: {}'.format(3), True, (200, 200, 200))

    window.draw(background_img, (0, 0))

    if info['conn_ok']:
        window.draw(conn_ok, (0, row(0)))
    else:
        window.draw(conn_error, (0, row(0)))
    window.draw(server_txt, (0, row(1)))
    window.draw(your_txt, (0, row(3)))
    window.draw(score_txt, (0, row(4)))
    window.render()
