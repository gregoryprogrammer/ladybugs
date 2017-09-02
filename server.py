#!env  python3
import os
import sys
import time
import json
import threading
import socketserver

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

print('Available ladybugs:', LADYBUGS_IDS)

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        print('Bug connection incoming')
        try:
            bug_id = str(self.request.recv(config.MSG_LEN), 'ascii')
            print('bug_id:', bug_id)

            if bug_id not in LADYBUGS_IDS:

                jdata = {'server_msg': 'Brak biedronki {}.'.format(bug_id)}
                tosend = bytes(json.dumps(jdata), 'ascii')
                self.request.sendall(tosend)

                print('bug {} unauthorized'.format(bug_id))
                return

            elif bug_id in meadow.bugs_ids():

                jdata = {'server_msg': 'Biedronka {} jest już zajęta przez kogoś innego!'.format(bug_id)}
                tosend = bytes(json.dumps(jdata), 'ascii')
                self.request.sendall(tosend)

                print('bug {} already controlled'.format(bug_id))
                return

            jdata = {'server_msg': 'Witaj na arenie!'}
            tosend = bytes(json.dumps(jdata), 'ascii')
            self.request.sendall(tosend)

            mainloop = meadow.add_bug(bug_id, 'Nowy', (0, 0))

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

                # send bug and arena info
                #
                tosend = bytes(json.dumps(bug_info), 'ascii')
                self.request.sendall(tosend)

                # waiting for instruction/order
                #
                order = str(self.request.recv(config.MSG_LEN), 'ascii')
                # print('Bug:', bug_id, 'order:', order)

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
ranking_pos = (1300, 25)

meadow.add_sweet((1, 1))
meadow.add_sweet((2, 2))
meadow.add_sweet((3, 3))
meadow.add_sweet((4, 3))
meadow.add_sweet((5, 3))
meadow.add_sweet((6, 3))
meadow.add_sweet((7, 3))

while window.loop():

    # logic
    #
    mmpos = pygame.mouse.get_pos()
    mmpos = mmpos[0] - meadow_pos[0], mmpos[1] - meadow_pos[1]

    meadow.update(config.FPS / 1000.0)
    highlighted_tile = meadow.highlight(mmpos)

    if window.mouse_just_pressed and highlighted_tile:
        meadow.add_sweet(highlighted_tile)

    ranking = meadow.get_ranking()
    ranking = reversed(sorted(ranking, key=lambda tup: tup[2]))

    # draw
    #
    for img, pos in meadow.images():
        abs_pos = meadow_pos[0] + pos[0], meadow_pos[1] + pos[1]
        window.draw(img, abs_pos)

    window.draw(ladybugs_txt, ranking_pos)
    for i, (bug_id, bug_name, score) in enumerate(ranking):
        tile = config.TILE
        bug_img = assets.get_bug_img(bug_id)
        bug_img = pygame.transform.scale(bug_img, (tile, tile))  # FIXME

        score_img = font.render('{}'.format(score), True, config.COLOR_WHITE)
        name_img = font.render('{}'.format(bug_name), True, config.COLOR_YELLOW)

        x = ranking_pos[0]
        y = ranking_pos[1] + (tile * 1.1) * (i + 1)
        y_score = y + tile / 2 - score_img.get_size()[1] / 2

        window.draw(bug_img, (x, y))
        window.draw(score_img, (x + tile * 2, y_score))
        window.draw(name_img, (x + tile * 4, y_score))

    # flip
    #
    window.render()

print('waiting for threads...')
print(server)
globalloop = False

server.shutdown()
server.server_close()
