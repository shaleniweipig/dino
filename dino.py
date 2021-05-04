import pygame
import neat
import os, random

pygame.font.init()

SCREEN_WIDTH = 850
SCREEN_HEIGHT = 500
SPEEND = 5
SCORE = 0

# Creating colors
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Images
# BG_IMG =
DINO_IMG = pygame.image.load(os.path.join('images', 'dino.png'))
CACTUS_IMG = pygame.image.load(os.path.join('images', 'cact1.png'))
# BASE_IMG = pygame.image.load(os.path.join('images', 'base.pgn'))
BG_IMG = pygame.image.load(os.path.join('images', 'bg.png'))

BASE_HEIGHT = 50
GEN = 0
# Setting up fonts
font = pygame.font.SysFont('Verdana', 60)
game_over = font.render('Game Over', True, BLACK)


class Dino:
    IMG = DINO_IMG
    ANIMATION_TIME = 5

    def __init__(self, x):
        self.x = x
        self.y = SCREEN_HEIGHT - BASE_HEIGHT - self.IMG.get_height()
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.tick_count = 0
        self.img = self.IMG

    def jump(self):
        if self.y < SCREEN_HEIGHT - BASE_HEIGHT- self.img.get_height():
            return
        self.vel = -10.5
        self.height = self.y
        self.tick_count = 0

    def move(self):
        self.tick_count += 1
        d = self.vel * self.tick_count + 0.15 * self.tick_count ** 2
        if d > 0:
            d = 0
        self.y = self.height + d

    def draw(self, win):
        win.blit(self.img, (self.x, self.y))

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Cactus:
    VEL = 5
    IMG = CACTUS_IMG

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.y = 0
        self.img = self.IMG
        self.set_height()
        self.passed = False

    def set_height(self):
        rand = random.randrange(13, 20)
        self.img = pygame.transform.scale(self.IMG,
                                          (self.IMG.get_width() * 10 // rand, self.IMG.get_height() * 10 // rand))
        self.y = SCREEN_HEIGHT - BASE_HEIGHT - self.img.get_height()

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.img, (self.x, self.y))

    def collide(self, dino):
        dino_mask = dino.get_mask()
        cactus_mask = pygame.mask.from_surface(self.IMG)
        offset = (int(self.x - dino.x), int(self.y - dino.y))
        point = dino_mask.overlap(cactus_mask, offset)
        if point:
            return True
        return False


class Base:
    VEL = 5
    # IMG = BASE_IMG

    def __init__(self):
        self.x1 = 0
        self.x2 = SCREEN_WIDTH
        # self.img = self.IMG

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + SCREEN_WIDTH < 0:
            self.x1 = self.x2 + SCREEN_WIDTH
        if self.x2 + SCREEN_WIDTH < 0:
            self.x2 = self.x1 + SCREEN_WIDTH

    # def draw(self, win):
    #     win.blit(self.img, (self.x1, SCREEN_HEIGHT - BASE_HEIGHT))
    #     win.blit(self.img, (self.x2, SCREEN_HEIGHT - BASE_HEIGHT))


def drawWindow(win, dinos, cactuses, gen, score):
    win.blit(BG_IMG, (0, 0))
    for d in dinos:
        d.draw(win)
    for c in cactuses:
        c.draw(win)
    gen_stat = font.render('GEN: ' + str(gen), 1, BLACK)
    score_stat = font.render('Score: ' + str(score), 1, BLACK)
    win.blit(gen_stat, (10, 10))
    win.blit(score_stat, (SCREEN_WIDTH - 10 - score_stat.get_width(), 10))
    pygame.display.update()


def main(genomes, config):
    global GEN
    GEN += 1
    ge = []
    dinos = []
    nets = []
    count_time = 0
    score = 0
    # dino = Dino(100)
    cactuses = [Cactus(850)]
    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    win.fill(WHITE)
    pygame.display.set_caption('Dino Game')
    clock = pygame.time.Clock()

    # Creating genomes
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        dinos.append(Dino(100))
        g.fitness = 0
        ge.append(g)
        nets.append(net)

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        # deleting cactus that is out off the window
        rm_count = 0
        for c in cactuses:
            if c.x < -c.img.get_width():
                rm_count += 1
        while rm_count:
            cactuses.pop(0)
            rm_count -= 1

        # Getting the idx of cactus the dino is facing
        idx = 0
        if dinos:
            if cactuses and cactuses[0].x + cactuses[0].img.get_width() < dinos[0].x:
                if not cactuses[0].passed:
                    score += 1
                    cactuses[0].passed = True
                idx = 1
        else:
            break

        # Setting output
        for i, d in enumerate(dinos):
            output = nets[i].activate((cactuses[idx].img.get_height(), cactuses[idx].x))
            if output[0] > 0.4:
                d.jump()

        i, n = 0, len(dinos)
        while i < n:
            if cactuses[idx].collide(dinos[i]):
                dinos.pop(i)
                ge.pop(i)
                nets.pop(i)
                n -= 1
            else:
                ge[i].fitness += 2
                i += 1

        # Appending new cactus
        count_time += 1
        rand = random.randrange(70, 150)
        if count_time >= rand:
            cactuses.append(Cactus(850))
            count_time = 0

        #Setting score
        # for c in cactuses:
        #     if not c.passed and dinos[0].x > c.x + c.img.get_width():
        #         score += 1
        #         c.passed = True
        # Move and draw
        for i, d in enumerate(dinos):
            ge[i].fitness += 0.1
            d.move()
        for c in cactuses:
            c.move()
        drawWindow(win, dinos, cactuses, GEN, score)


def run(config_file):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(main, 30)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
