import os
import pygame

import config
import assets

MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]

def create_background(size, tile):
    x_tiles, y_tiles = size[0] // tile, size[1] // tile
    width = x_tiles * tile
    height = y_tiles * tile
    background = pygame.Surface((width, height))
    background.fill(config.COLOR_GRAY)

    for ty in range(0, y_tiles):
        for tx in range(0, x_tiles):
            x = tx * tile
            y = ty * tile
            pygame.draw.line(background, config.COLOR_GRAY_LIGHT, (x, 0), (x, size[1]))
            pygame.draw.line(background, config.COLOR_GRAY_LIGHT, (0, y), (size[0], y))

    pygame.draw.line(background, config.COLOR_GRAY_LIGHT, (0, height - 1), (width, height - 1))
    pygame.draw.line(background, config.COLOR_GRAY_LIGHT, (width - 1, 0), (width - 1, height))

    return background

def printfr(text):
    L = len(text)
    print('.-' + '-' * L + '-.')
    print('| ' + text + ' |')
    print('\'-' + '-' * L + '-\'')

class Window(object):

    def __init__(self, **kwargs):
        self.running = True
        pygame.init()
        pygame.display.set_caption(kwargs.get('name'))
        self.screen = pygame.display.set_mode(
            kwargs.get('size'),
            pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE
        )
        self.clock = pygame.time.Clock()
        self.mouse_just_pressed = False
        self.background = pygame.Surface(kwargs.get('size'))
        self.background.fill((0, 0, 0))

    def __del__(self):
        pygame.quit()

    def is_open(self):
        return self.running

    def close(self):
        self.running = False

    def loop(self):
        self.mouse_just_pressed = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
            elif event.type == pygame.KEYDOWN and event.key in (pygame.K_q, pygame.K_ESCAPE):
                self.close()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_just_pressed = True

        self.screen.blit(self.background, (0, 0))
        return self.running

    def draw(self, surface, xy):
        self.screen.blit(surface, xy)

    def render(self):
        # flip
        #
        pygame.display.flip()


class Button(object):
    def __init__(self, pos, size, text, callback):
        self.pos = pos
        self.size = size
        self.text = text
        self.callback = callback
        self.img = pygame.Surface(size)
        self.img_hovered = pygame.Surface(size)
        self.img.fill(config.COLOR_GRAY_LIGHT)
        self.img_hovered.fill(config.COLOR_YELLOW)

        font = assets.load_font('Ubuntu-Regular.ttf', 24)
        txt = font.render(text, True, config.COLOR_BLACK)
        self.img.blit(txt, ((size[0] - txt.get_width()) // 2, (size[1] - txt.get_height()) // 2))
        self.img_hovered.blit(txt, ((size[0] - txt.get_width()) // 2, (size[1] - txt.get_height()) // 2))

    def collides(self, pos):
        cx = self.pos[0] <= pos[0] <= (self.pos[0] + self.size[0])
        cy = self.pos[1] <= pos[1] <= (self.pos[1] + self.size[1])
        return cx and cy


class Bug(object):

    def __init__(self, **kwargs):
        self.bug_id = kwargs.get('bug_id')
        self.bug_name = kwargs.get('bug_name')
        self.prev_tile_pos = (0, 0)
        self.tile_pos = (0, 0)
        self.move_time = 0
        self.direction = 'N'
        self.score = 0

    def update(self, dt):
        self.move_time += dt
        self.move_time = min(config.BUG_DELAY, self.move_time)

class Meadow(object):

    def __init__(self, **kwargs):
        self.tile = kwargs.get('tile')
        self.bugs = {}
        self.sweets = []
        self.walls = []

        size = kwargs.get('size')
        self.x_tiles = size[0] // self.tile
        self.y_tiles = size[1] // self.tile

        self.size = self.x_tiles * self.tile, self.y_tiles * self.tile

        for x in range(-1, self.x_tiles + 1):
            self.walls.append((x, -1))
            self.walls.append((x, self.y_tiles))

        for y in range(-1, self.y_tiles + 1):
            self.walls.append((-1, y))
            self.walls.append((self.x_tiles, y))

        self.background_img = create_background(self.size, self.tile)
        self.sweet_img = pygame.transform.scale(
            assets.load_image('sweet.png'), (self.tile, self.tile)
        )
        self.selection = None
        self.selection_img = assets.create_highlight(self.tile, (200, 200, 0))

    def update(self, dt):
        for bug_id, bug in self.bugs.items():
            bug.update(dt)

    def add_sweet(self, tile_pos):
        if tile_pos not in self.sweets:
            self.sweets.append(tile_pos)

    def delete_sweet(self, sweet):
        self.sweets.remove(sweet)

    def clear_sweets(self):
        self.sweets = []

    def add_bug(self, bug_id, bug_name, tile_pos):
        if bug_id in self.bugs.keys():
            return False
        print('New bug:', bug_id, bug_name)
        bug = Bug(bug_id=bug_id, bug_name=bug_name)
        bug.prev_tile_pos = tile_pos
        bug.tile_pos = tile_pos
        self.bugs[bug_id] = bug
        return True

    def get_bug(self, bug_id):
        return self.bugs.get(bug_id)

    def get_tile_info(self, tile):
        tile_info = ''
        for wall in self.walls:
            if wall == tile and not '#' in tile_info:
                tile_info += '#'
        for sweet in self.sweets:
            if sweet == tile and not '$' in tile_info:
                tile_info += '$'
        return tile_info

    def get_ranking(self):
        ranking = []
        bugs = self.bugs.copy()
        for bug_id, bug in bugs.items():
            ranking.append((bug_id, bug.bug_name, bug.score))
        return ranking

    def bugs_ids(self):
        return self.bugs.keys()

    def delete_bug(self, bug_id):
        if bug_id not in self.bugs.keys():
            return False
        del self.bugs[bug_id]

    def move_bug(self, bug_id, direction):
        bug = self.bugs.get(bug_id)
        if not bug:
            return False
        pos = bug.tile_pos
        if direction in 'E':
            bug.tile_pos = pos[0] + 1, pos[1] + 0
        elif direction in 'W':
            bug.tile_pos = pos[0] - 1, pos[1] + 0
        elif direction in 'N':
            bug.tile_pos = pos[0] + 0, pos[1] - 1
        elif direction in 'S':
            bug.tile_pos = pos[0] + 0, pos[1] + 1

        bug.direction = direction
        bug.move_time = 0

    def reset(self):
        self.sweets = []
        bugs = self.bugs.copy()
        for bug_id, bug in bugs.items():
            bug.score = 0
            bug.tile_pos = (0, 0)
        self.bugs = bugs
        print('it works')

    def highlight(self, pos):
        if not 0 <= pos[0] <= self.size[0] or not 0 <= pos[1] <= self.size[1]:
            self.selection = None
        else:
            self.selection = pos[0] // self.tile, pos[1] // self.tile
        return self.selection

    def images(self):
        yield (self.background_img, (0, 0))

        for sweet in self.sweets:
            yield (self.sweet_img, (sweet[0] * self.tile, sweet[1] * self.tile))

        bugs = self.bugs.copy()
        for bug_id, bug in bugs.items():
            prev_bug_pos = bug.prev_tile_pos[0] * self.tile, bug.prev_tile_pos[1] * self.tile
            bug_pos = bug.tile_pos[0] * self.tile, bug.tile_pos[1] * self.tile

            t = bug.move_time
            bx = prev_bug_pos[0] + (bug_pos[0] - prev_bug_pos[0]) * (t / config.BUG_DELAY)
            by = prev_bug_pos[1] + (bug_pos[1] - prev_bug_pos[1]) * (t / config.BUG_DELAY)

            bug_pos = (bx, by)

            bug_img = assets.get_bug_img(bug_id)
            bug_img = pygame.transform.scale(bug_img, (self.tile, self.tile))

            angle = 0
            if bug.direction == 'W':
                angle = 90
            elif bug.direction == 'S':
                angle = 180
            elif bug.direction == 'E':
                angle = 270

            bug_img = pygame.transform.rotate(bug_img, angle)

            yield (bug_img, bug_pos)

        if self.selection:
            pos = self.selection[0] * self.tile, self.selection[1] * self.tile
            yield (self.selection_img, pos)
