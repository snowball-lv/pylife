import pygame
import random

pygame.init()
pygame.font.init()

class Entity:

    def __init__(self, game):
        self.game = game
        self.age = 0.0

    def update(self, delta):
        self.age += delta

    def draw(self):
        pass

class Actor(Entity):
    
    ID_COUNTER = 1

    def get_next_id():
        id = Actor.ID_COUNTER
        Actor.ID_COUNTER += 1
        return id

    def __init__(self, game):
        super().__init__(game)
        self.id = Actor.get_next_id()

class Game:

    def __init__(self):
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height))
        self.running = False
        self.font = pygame.font.SysFont(None, 24)
        self.headless = False
        self.ticks = 0
        self.actors = []
        for i in range(10):
            self.actors.append(Actor(self))

    def update(self, delta):
        self.ticks += 1
        for actor in self.actors:
            actor.update(delta)

    def on_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                print("Toggling headless mode")
                self.headless = not self.headless
                return True
        return False
    
    def draw_text(self, text, pos, color = "ivory"):
        surface = self.font.render(text, True, color)
        self.screen.blit(surface, pos)

    def draw(self):
        self.screen.fill(pygame.Color(40, 40, 40))
        for i, actor in enumerate(self.actors):
            text = "Actor {}".format(actor.id)
            pos = pygame.Vector2(50, 100) + i * pygame.Vector2(0, 24)
            self.draw_text(text, pos)
        self.draw_text("Ticks {}".format(self.ticks), (10, 10))

    def run(self):
        self.clock = pygame.time.Clock()
        self.running = True
        step_size = 1.0 / 60
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
            if self.headless:
                start = pygame.time.get_ticks()
                while pygame.time.get_ticks() - start < 10:
                    self.update(step_size)
            else:
                self.update(delta)
            self.draw()
            pygame.display.flip()

game = Game()
game.run()

pygame.quit()
