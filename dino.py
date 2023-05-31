import os
import time
import pygame
from random import randint
from collections import deque as stack


class Game:
    FPS = 60
    ROOT_WIDTH = 600
    ROOT_HEIGHT = 500

    def __init__(self) -> None:
        pygame.init()

        self.root = pygame.display.set_mode((self.ROOT_WIDTH, self.ROOT_HEIGHT))
        pygame.display.set_caption('Flappy Dino')

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont(None, 32, bold=True)

        self.images = self.load_images()
        self.images["background"] = self.images["background"].convert()

        self.dino = Dino(50, int(self.ROOT_WIDTH / 2 - Dino.HEIGHT / 2), self.images['dino'])

        self.pipes = stack()

        self.score = 0

        self.running = True
        self.paused = False

    @staticmethod
    def load_images():
        def load(img):
            return pygame.image.load(os.path.join(os.path.dirname(__file__), img))

        return {'background': load('background.png'),
                'dino': load('dino.png')}

    def loop(self):
        while self.running:
            self.clock.tick(self.FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                    break

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    self.paused = not self.paused
                    if self.paused:
                        Pipe.pause()

                    else:
                        Pipe.unpause()

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.dino.jump()

            if self.paused:
                continue

            elif Pipe.interval():
                pipe = Pipe((self.ROOT_WIDTH, self.ROOT_HEIGHT))
                self.pipes.append(pipe)

            self.collision()

            if self.pipes and not self.pipes[0].visible:
                self.pipes.popleft()

            self.draw()

            for pipe in self.pipes:
                if pipe.x + Pipe.WIDTH < self.dino.x and not pipe.scored:
                    self.score += 1
                    pipe.scored = True

            score = self.font.render(str(self.score), True, (000, 000, 000))
            score_x = self.ROOT_WIDTH / 2 - score.get_width() / 2
            self.root.blit(score, (score_x, 10))

            pygame.display.update()

    def collision(self):
        collision = any(pipe.collision(self.dino) for pipe in self.pipes)
        if collision or 0 >= self.dino.y or self.dino.y >= self.ROOT_HEIGHT - Dino.HEIGHT:
            self.running = False

    def draw(self):
        self.root.blit(self.images['background'], (0, 0))

        for pipe in self.pipes:
            pipe.update()
            self.root.blit(pipe.image, pipe.rect)

        self.dino.update()
        self.root.blit(self.dino.image, self.dino.rect)

    def close(self):
        pygame.quit()
        return self.score


class Dino(pygame.sprite.Sprite):
    WIDTH = 32
    HEIGHT = 32

    def __init__(self, x, y, image) -> None:
        self.x = x
        self.y = y

        self.climbing = 3

        image = pygame.transform.scale(image, (self.WIDTH, self.HEIGHT))
        self.imageDino = image

    def update(self):
        if self.climbing > 0:
            self.y -= 3
            self.climbing -= 1
        else:
            self.y += 1.5

    def jump(self):
        self.climbing = 20

    @property
    def image(self):
        return self.imageDino

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, Dino.WIDTH, Dino.HEIGHT)


class Pipe(pygame.sprite.Sprite):
    WIDTH = 80
    clock = 0

    def __init__(self, root) -> None:
        self.scored = False

        self.x = root[0]

        self.image = pygame.surface.Surface((self.WIDTH, root[1]))
        self.image.convert()
        self.image.set_colorkey((0, 0, 0, 0))
        self.image.fill((0, 0, 0, 0))

        self.gapY = randint(30, root[1] - 130)

        up = pygame.surface.Surface((self.WIDTH, self.gapY))
        up.convert()
        up.fill((37, 150, 190))

        down = pygame.surface.Surface((self.WIDTH, root[1] - self.gapY - 90 if root[1] - self.gapY - 100 > 0 else 0))
        down.convert()
        down.fill((37, 150, 190))

        self.image.blit(up, (0, 0))
        self.image.blit(down, (0, self.gapY + 90))

        self.check = 'root'

    @property
    def rect(self):
        if self.check == 'root':
            return pygame.Rect(self.x, 0, Pipe.WIDTH, 600)

        elif self.check == 'up':
            return pygame.Rect(self.x, 0, Pipe.WIDTH, self.gapY)

        elif self.check == 'down':
            return pygame.Rect(self.x, self.gapY + 100, Pipe.WIDTH, 600)

    def collision(self, dino):
        self.check = 'up'
        up = pygame.sprite.collide_mask(self, dino)

        self.check = 'down'
        down = pygame.sprite.collide_mask(self, dino)

        self.check = 'root'

        return up or down

    def update(self):
        self.x -= 3

    @property
    def visible(self):
        return -self.WIDTH < self.x

    @classmethod
    def interval(cls):
        if time.time() - cls.clock > 3:
            cls.clock = time.time()
            return True

        else:
            return False

    @classmethod
    def pause(cls):
        cls.diff = time.time() - cls.clock

    @classmethod
    def unpause(cls):
        cls.clock = time.time() - cls.diff


if __name__ == '__main__':
    game = Game()
    game.loop()
    print(f'Score: {game.close()}')
