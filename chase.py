import pygame
import random
import enum
import heapq
from brain import Brain

pygame.init()
pygame.font.init()

def random_color():
    return pygame.Color(
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255))


class Strain:

    ID_COUNTER = 1

    def __init__(self):
        self.brain = None
        self.id = 0
        self.color = pygame.Color("black")

    def basic():
        strain = Strain()
        strain.brain = Brain.basic(8, 3, 64)
        strain.id = Strain.ID_COUNTER
        Strain.ID_COUNTER += 1
        strain.color = random_color()
        return strain

    def split(self):
        child = Strain()
        child.brain = self.brain.copy()
        child.brain.mutate(0.20)
        child.id = self.id
        child.color = self.color
        return child

class Actor:

    def __init__(self):
        self.pos = pygame.Vector2()
        self.speed_factor = 1.0
        self.size = 16
        self.strain = None
        self.age = 0.0

    def update(self, delta):
        self.age += delta

    def reset(self):
        self.strain = None
        self.age = 0.0

    def get_rect(self):
        hsize = self.size / 2
        return pygame.Rect(self.pos.x - hsize, self.pos.y - hsize,
                           self.size, self.size)
    
class State(enum.Enum):
    NONE = 0
    CHASING = 1
    END = 2

class Game:

    def __init__(self):
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height))
        self.running = False
        self.font = pygame.font.SysFont(None, 24)
        self.camera_offset = pygame.Vector2()
        self.field_width = 512
        self.field_height = 512
        self.field = pygame.Rect(
            (self.screen_width - self.field_width) / 2,
            (self.screen_height - self.field_height) / 2,
            self.field_width, self.field_height)
        self.predator = Actor()
        self.predator.color = "maroon"
        self.prey = Actor()
        self.state = State.NONE
        self.predator_radius = 16
        self.movement_speed = 100 * 10
        self.results = []
        self.best = []
        self.generation = 0
        self.headless = False
        self.reseed()

    def reseed(self):
        self.waiting = [Strain.basic() for _ in range(1000)]

    def draw_text(self, text, pos):
        surface = self.font.render(text, True, "ivory")
        self.screen.blit(surface, pos)

    def draw(self):
        self.screen.fill("black")
        pygame.draw.rect(self.screen, "ivory", self.field)
        self.draw_text("{} waiting".format(len(self.waiting)), (10, 10))
        if self.state == State.NONE:
            pass
        elif self.state == State.CHASING:
            pygame.draw.rect(self.screen, self.prey.strain.color, self.prey.get_rect())
            pygame.draw.circle(self.screen, self.predator.color,
                               self.predator.pos, self.predator_radius)
            self.draw_text("Prey age {}".format(round(self.prey.age, 2)), (10, 30))
        self.draw_text("Generation {}".format(self.generation), (10, 50))
        if self.best:
            offset = 200
            self.draw_text("Best results", (10, offset))
            offset += 20
            for i in range(len(self.best)):
                age, _ = self.best[i]
                self.draw_text("{}".format(round(age, 2)), (10, offset))
                offset += 20
        ids = [strain.id for _, strain in self.best]
        self.draw_text("Strains {}".format(len(set(ids))), (10, 70))


    def start_simulation(self, strain):
        # set prey
        self.prey.reset()
        self.prey.strain = strain
        self.prey.pos = pygame.Vector2(self.field.center)
        self.prey.pos.x = self.field.right - 32
        # set predator
        self.predator.pos = pygame.Vector2(self.field.center)
        self.predator.pos.x = self.field.left + 32
        # start simulation
        self.state = State.CHASING

    def kill_prey(self):
        self.state = State.NONE
        self.results.append((self.prey.age, self.prey.strain))

    def update(self, delta):
        if self.state == State.NONE:
            if self.waiting:
                strain = self.waiting[0]
                self.waiting.remove(strain)
                self.start_simulation(strain)
            else:
                self.state = State.END
        elif self.state == State.CHASING:
            dist = self.prey.pos - self.predator.pos
            # predator
            if dist.length() < self.predator_radius:
                self.kill_prey()
                return
            else:
                dir = dist.normalize()
                self.predator.pos += dir * self.movement_speed * delta * 0.5
            # prey
            self.prey.update(delta)
            inputs = self.prey.strain.brain.new_inputs()
            inputs[0] = self.prey.pos.x
            inputs[1] = self.prey.pos.y
            inputs[2] = self.predator.pos.x
            inputs[3] = self.predator.pos.y
            inputs[4] = self.field.left
            inputs[5] = self.field.top
            inputs[6] = self.field.right
            inputs[7] = self.field.bottom
            outputs = self.prey.strain.brain.process(inputs)
            dir = pygame.Vector2(outputs[0], outputs[1]).normalize()
            self.prey.pos += dir * self.movement_speed * outputs[2] * delta
            if not self.field.collidepoint(self.prey.pos):
                self.kill_prey()
                return
        elif self.state == State.END:
            pool = self.best + self.results
            self.best = heapq.nlargest(100, pool, lambda x: x[0])
            self.results.clear()
            for _, strain in self.best:
                for _ in range(2):
                    child = strain.split()
                    self.waiting.append(child)
            self.generation += 1
            self.state = State.NONE

    def on_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                print("Toggling headless mode")
                self.headless = not self.headless
                return True
            elif event.key == pygame.K_k:
                print("Killing current prey")
                if self.state == State.CHASING:
                    self.kill_prey()
        return False

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
