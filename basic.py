import pygame
from brain import Brain

pygame.init()

class Game:

    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600))
        self.running = False
        pass

    def draw(self):
        pass

    def update(self, delta):
        pass

    def on_input(self, event):
        return False

    def run(self):
        self.clock = pygame.time.Clock()
        self.running = True
        while self.running:
            delta = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if self.on_input(event):
                    pass
                elif event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_q]:
                        self.running = False
            self.update(delta)
            self.draw()
            pygame.display.flip()

game = Game()
game.run()

pygame.quit()
