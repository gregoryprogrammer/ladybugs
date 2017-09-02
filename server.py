#!env  python3
import os
import sys
import time
import json
import random
import threading
import socketserver

from enum import Enum

import pygame
import config
import assets
import utils

LADYBUGS_DIR = os.path.join(utils.MAIN_DIR, 'assets', 'ladybugs')
LADYBUGS_IMAGES = os.listdir(LADYBUGS_DIR)
LADYBUGS_IDS = [os.path.splitext(bug)[0] for bug in LADYBUGS_IMAGES]

LADYBUGS_ORDERS = ('N', 'S', 'W', 'E', 'X')

MEADOW_SIZE = int(config.SERVER_WINDOW_SIZE[0] * 0.75), int(config.SERVER_WINDOW_SIZE[1] * 0.75)

window = utils.Window(name='LadyBugs - server', size=config.SERVER_WINDOW_SIZE)
meadow = utils.Meadow(size=MEADOW_SIZE, tile=config.TILE)

globalloop = True

class ArenaState(Enum):
    FREEGAME = 0
    CHALLENGE_WAIT = 1
    CHALLENGE = 2
    PAUSE = 3

arena_state = ArenaState.PAUSE

print('Available ladybugs:', LADYBUGS_IDS)

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        global arena_state
        print('Bug connection incoming')
        try:
            recv = str(self.request.recv(config.MSG_LEN), 'utf8')
            print('RECV = ', recv)
            try:
                bug_id, bug_name = recv.split(',')
            except:
                return
            print('bug_id:', bug_id)

            if arena_state == ArenaState.CHALLENGE:
                jdata = {'server_msg': 'Trwają zawody. Poczekaj na następną rundę.'}
                tosend = bytes(json.dumps(jdata), 'utf8')
                self.request.sendall(tosend)
                return

            if bug_id not in LADYBUGS_IDS:

                jdata = {'server_msg': 'Brak biedronki {}.'.format(bug_id)}
                tosend = bytes(json.dumps(jdata), 'utf8')
                self.request.sendall(tosend)

                print('bug {} unauthorized'.format(bug_id))
                return

            elif bug_id in meadow.bugs_ids():

                jdata = {'server_msg': 'Biedronka {} jest już zajęta przez kogoś innego!'.format(bug_id)}
                tosend = bytes(json.dumps(jdata), 'utf8')
                self.request.sendall(tosend)

                print('bug {} already controlled'.format(bug_id))
                return

            jdata = {'server_msg': 'Witaj na arenie!'}
            tosend = bytes(json.dumps(jdata), 'utf8')
            self.request.sendall(tosend)

            mainloop = meadow.add_bug(bug_id, bug_name)

            while mainloop and globalloop:
                time.sleep(config.BUG_DELAY)

                bug = meadow.get_bug(bug_id)

                bug.prev_tile_pos = bug.tile_pos
                bug.move_time = 0

                tile_pos = bug.tile_pos
                tile_N = tile_pos[0] + 0, tile_pos[1] - 1
                tile_S = tile_pos[0] + 0, tile_pos[1] + 1
                tile_W = tile_pos[0] - 1, tile_pos[1] + 0
                tile_E = tile_pos[0] + 1, tile_pos[1] + 0

                tile_N_info = meadow.get_tile_info(tile_N)
                tile_S_info = meadow.get_tile_info(tile_S)
                tile_W_info = meadow.get_tile_info(tile_W)
                tile_E_info = meadow.get_tile_info(tile_E)

                bug_info = {}
                bug_info['sweets'] = meadow.sweets
                bug_info['position'] = bug.tile_pos
                bug_info['N'] = tile_N_info
                bug_info['S'] = tile_S_info
                bug_info['W'] = tile_W_info
                bug_info['E'] = tile_E_info
                bug_info['server_msg'] = 'Hello'
                bug_info['score'] = bug.score

                if arena_state == ArenaState.FREEGAME:
                    bug_info['server_msg'] = 'Ćwiczenia'
                    bug_info['arena_state'] = 'freegame'
                elif arena_state == ArenaState.PAUSE:
                    bug_info['server_msg'] = 'Pauza'
                    bug_info['arena_state'] = 'pause'
                elif arena_state == ArenaState.CHALLENGE_WAIT:
                    bug_info['server_msg'] = 'Czekam na zawodników'
                    bug_info['arena_state'] = 'challenge_wait'
                elif arena_state == ArenaState.CHALLENGE:
                    bug_info['server_msg'] = 'Trwają zawody!'
                    bug_info['arena_state'] = 'challenge'

                # send bug and arena info
                #
                tosend = bytes(json.dumps(bug_info), 'utf8')
                self.request.sendall(tosend)

                # waiting for instruction/order
                #
                order = str(self.request.recv(config.MSG_LEN), 'utf8')
                # print('Bug:', bug_id, 'order:', order)

                if arena_state in (ArenaState.PAUSE, ArenaState.CHALLENGE_WAIT):
                    continue

                if order not in LADYBUGS_ORDERS:
                    print('Bug:', bug_id, 'unrecognized order:', order)
                    continue

                if order in 'NSWE':
                    bug.direction = order

                if order == 'N' and not '#' in tile_N_info:
                    tile_pos = tile_N
                elif order == 'S' and not '#' in tile_S_info:
                    tile_pos = tile_S
                elif order == 'W' and not '#' in tile_W_info:
                    tile_pos = tile_W
                elif order == 'E' and not '#' in tile_E_info:
                    tile_pos = tile_E

                tile_X_info = meadow.get_tile_info(tile_pos)

                if '$' in tile_X_info:
                    meadow.delete_sweet(tile_pos)
                    bug.score += 1

                bug.tile_pos = tile_pos

                # cur_thread = threading.current_thread()
        except:
            print(sys.exc_info())
        meadow.delete_bug(bug_id)
        print('finally')

socketserver.ThreadingTCPServer.allow_reuse_address = True
server = socketserver.ThreadingTCPServer(config.SERVER_ADDRESS, ThreadedTCPRequestHandler)

server_thread = threading.Thread(target=server.serve_forever)
server_thread.daemon = True
server_thread.start()

font = assets.load_font('Ubuntu-Regular.ttf', 24)
ladybugs_txt = font.render('Ranking biedronek', True, config.COLOR_WHITE)

meadow_pos = (25, 25)
ranking_pos = (int(0.8 * config.SERVER_WINDOW_SIZE[0]), 25)

def arena_pause():
    global arena_state
    arena_state = ArenaState.PAUSE

def arena_start():
    global arena_state
    arena_state = ArenaState.FREEGAME

def arena_wait():
    global arena_state
    arena_state = ArenaState.CHALLENGE_WAIT

def arena_challenge():
    global arena_state
    arena_state = ArenaState.CHALLENGE

def map_one():
    sweets = []
    while len(sweets) < 10:
        x = random.random() * meadow.x_tiles
        y = random.random() * meadow.y_tiles
        x = int(x)
        y = int(y)
        if (x, y) not in sweets:
            sweets.append((x, y))
    for sweet in sweets:
        meadow.add_sweet(sweet)

def map_two():
    meadow.clear_sweets()
    sweets = []
    for x in range(4, meadow.x_tiles - 4, 2):
        for y in range(2, meadow.y_tiles - 2, 2):
            sweets.append((x, y))

    random.shuffle(sweets)
    for sweet in sweets:
        meadow.add_sweet(sweet)

def map_three():
    meadow.clear_sweets()
    sweets = []
    for x in range(5, meadow.x_tiles - 5):
        for y in range(2, meadow.y_tiles, 3):
            sweets.append((x, y))

    random.shuffle(sweets)
    for sweet in sweets:
        meadow.add_sweet(sweet)

BUTTON_SIZE = (200, 50)
buttons = []

buttons.append(utils.Button((25, 700), BUTTON_SIZE, 'RESET', meadow.reset))
buttons.append(utils.Button((25, 760), BUTTON_SIZE, 'TRENING', arena_start))
buttons.append(utils.Button((25, 820), BUTTON_SIZE, 'PAUSE', arena_pause))

buttons.append(utils.Button((250, 700), BUTTON_SIZE, 'WAIT', arena_wait))
buttons.append(utils.Button((250, 760), BUTTON_SIZE, 'CHALLENGE', arena_challenge))

buttons.append(utils.Button((550, 700), BUTTON_SIZE, 'RANDOM 10', map_one))
buttons.append(utils.Button((550, 760), BUTTON_SIZE, 'MAPA 2', map_two))
buttons.append(utils.Button((550, 820), BUTTON_SIZE, 'MAPA 3', map_three))

while window.loop():

    # logic
    #
    mouse_pos = pygame.mouse.get_pos()
    mmpos = mouse_pos[0] - meadow_pos[0], mouse_pos[1] - meadow_pos[1]

    meadow.update(config.FPS / 1000.0)
    highlighted_tile = meadow.highlight(mmpos)

    if window.mouse_just_pressed and highlighted_tile:
        meadow.add_sweet(highlighted_tile)

    # check buttons
    if window.mouse_just_pressed:
        for button in buttons:
            print('check button', button)
            if button.collides(mouse_pos):
                button.callback()

    ranking = meadow.get_ranking()
    ranking = reversed(sorted(ranking, key=lambda tup: tup[2]))

    # draw
    #
    for img, pos in meadow.images():
        abs_pos = meadow_pos[0] + pos[0], meadow_pos[1] + pos[1]
        window.draw(img, abs_pos)

    window.draw(ladybugs_txt, ranking_pos)
    for i, (bug_id, bug_name, score) in enumerate(ranking):
        tile = config.TILE // 2
        bug_img = assets.get_bug_img(bug_id)
        bug_img = pygame.transform.scale(bug_img, (tile, tile))  # FIXME

        score_img = font.render('{}'.format(score), True, config.COLOR_WHITE)
        name_img = font.render('{}'.format(bug_name), True, config.COLOR_YELLOW)

        x = ranking_pos[0]
        y = ranking_pos[1] + tile + (tile * 1.1) * (i + 1)
        y_score = y + tile / 2 - score_img.get_size()[1] / 2

        window.draw(bug_img, (x, y))
        window.draw(score_img, (x + tile * 2, y_score))
        window.draw(name_img, (x + tile * 4, y_score))

    for button in buttons:
        if button.collides(mouse_pos):
            window.draw(button.img_hovered, button.pos)
        else:
            window.draw(button.img, button.pos)

    # flip
    #
    window.render()

print('waiting for threads...')
print(server)
globalloop = False

server.shutdown()
server.server_close()
