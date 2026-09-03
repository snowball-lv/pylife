import pygame
from brain import Brain
import random
import math

pygame.init()

def random_color():
    return pygame.Color(
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255))

class Entity:
    def __init__(self, game):
        self.game = game
        self.pos = pygame.Vector2()
        self.size = 4
        self.color = random_color()
        self.age = 0.0
        pass
    def update(self, delta):
        self.age += delta
    def draw(self):
        rect = pygame.Rect(
            self.pos.x - self.size / 2,
            self.pos.y - self.size / 2,
            self.size, self.size)
        pygame.draw.rect(self.game.screen, self.color, rect)

class Food(Entity):

    def __init__(self, game):
        super().__init__(game)
        self.color = pygame.Color(0, 100, 0)
        self.radius = 100
        self.max_in_radius = 4
        self.counter = 0.0

    # def update(self, delta):
        # self.counter += delta
        # if self.counter > 10:
        #     self.counter = 0.0
        #     food = self.game.get_food()
        #     neighbors = [f for f in food
        #                  if (f.pos - self.pos).length() < self.radius]
        #     if len(neighbors) < self.max_in_radius:
        #         new_food = Food(self.game)
        #         pos = pygame.Vector2()
        #         rads = random.random() * 2 * math.pi
        #         pos.x = math.cos(rads)
        #         pos.y = math.sin(rads)
        #         pos *= random.random() * self.radius
        #         new_food.pos = self.pos + pos
        #         self.game.add_entity(new_food)

    def draw(self):
        super().draw()
        # pygame.draw.circle(self.game.screen, "red", self.pos, self.radius, 1)

class Actor(Entity):

    def __init__(self, game):
        super().__init__(game)
        self.brain = None
        self.max_speed = 100
        self.food = 3.0
        self.size = 8

    def draw(self):
        rect = pygame.Rect(
            self.pos.x - self.size / 2,
            self.pos.y - self.size / 2,
            self.size, self.size)
        pygame.draw.rect(self.game.screen, self.color, rect)
        food = self.game.get_food()
        food = sorted(food, key = lambda f: (f.pos - self.pos).length())
        for i in range(1):
            if i < len(food):
                pygame.draw.line(self.game.screen, "red", self.pos, food[i].pos)

    def consume(self, food):
        self.game.consume(self, food)
        self.food += 3

    def process(self, delta):
        inputs = []
        # field size
        inputs.append(self.game.field.rect.left)
        inputs.append(self.game.field.rect.right)
        inputs.append(self.game.field.rect.top)
        inputs.append(self.game.field.rect.bottom)
        # position
        inputs.append(self.pos.x)
        inputs.append(self.pos.y)
        inputs.append(self.max_speed)
        # stats
        inputs.append(self.food)
        # food
        food = self.game.get_food()
        food = sorted(food, key = lambda f: (f.pos - self.pos).length())
        inputs.append(food[0].pos.x)
        inputs.append(food[0].pos.y)
        outputs = self.brain.process(inputs)
        # --- updates
        # move
        dir = pygame.Vector2(outputs[0], outputs[1]).normalize()
        self.pos += dir * self.max_speed * outputs[2] * delta
        # consume
        for f in self.game.get_food():
            if (f.pos - self.pos).length() < self.size / 2:
                self.consume(f)

    def update(self, delta):
        self.food -= delta
        if self.brain:
            self.process(delta)
        if self.food < 0.0:
            self.game.die(self)

    def split(self):
        child = Actor(self.game)
        child.brain = self.brain.copy()
        child.brain.mutate(0.2)
        child.color = self.color
        return child

class Field:

    def __init__(self, game):
        self.game = game
        w, h = game.screen.get_size()
        self.rect = pygame.Rect(50, 50, w - 100, h - 100)

    def draw(self):
        pygame.draw.rect(self.game.screen, "ivory", self.rect)

    def get_rand_pos(self):
        x = random.randint(self.rect.left, self.rect.right)
        y = random.randint(self.rect.top, self.rect.bottom)
        return pygame.Vector2(x,  y)
    
    def is_inside(self, point):
        return self.rect.collidepoint(point)

class Game:

    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600))
        self.running = False
        self.field = Field(self)
        self.headless = False
        self.entities = []
        self.dead_actors = []
        self.spawn_queue = []
        self.remove_queue = []
        self.waiting = []
        self.best = []
        self.reseed()

    def add_entity(self, entity):
        self.spawn_queue.append(entity)

    def get_food(self):
        return [e for e in self.entities if isinstance(e, Food)]
    
    def get_actors(self):
        return [e for e in self.entities if isinstance(e, Actor)]
    
    def consume(self, actor, food):
        self.remove_queue.append(food)

    def die(self, actor):
        self.remove_queue.append(actor)
        self.dead_actors.append(actor)

    def reseed(self):
        self.remove_queue.clear()
        self.dead_actors.clear()
        self.entities.clear()
        self.spawn_queue.clear()
        # actors
        for i in range(1000):
            actor = Actor(self)
            actor.pos = self.field.get_rand_pos()
            actor.brain = Brain.basic(11, 3, 16)
            self.waiting.append(actor)
        # food
        for i in range(100):
            food = Food(self)
            food.pos = self.field.get_rand_pos()
            self.entities.append(food)
        self.next_actor()

    def draw(self):
        self.screen.fill("black")
        self.field.draw()
        for entity in self.entities:
            entity.draw()

    def next_actor(self):
        if len(self.waiting) == 0:
            print("Out of waiting actors, creating new generation")
            self.generate_new_actors()
        actor = self.waiting[0]
        self.waiting.remove(actor)
        self.entities.append(actor)
        # regenerate food
        for _ in range(100 - len(self.get_food())):
            food = Food(self)
            food.pos = self.field.get_rand_pos()
            self.entities.append(food)
        print("{} actors waiting".format(len(self.waiting)))

    def generate_new_actors(self):
        pool = self.dead_actors + self.best
        self.dead_actors.clear()
        best = sorted(pool, key = lambda a: a.age, reverse = True)
        for i in range(20):
            actor = best[i]
            for _ in range(2):
                child = actor.split()
                child.pos = self.field.get_rand_pos()
                self.waiting.append(child)

    def update(self, delta):
        if len(self.get_actors()) == 0:
            print("Out of actors, next actor's turn")
            self.next_actor()
        for entity in self.entities:
            entity.update(delta)
            if isinstance(entity, Actor):
                if not self.field.is_inside(entity.pos):
                    self.die(entity)
        # housekeeping
        for entity in self.spawn_queue:
            self.entities.append(entity)
        self.spawn_queue.clear()
        for entity in self.remove_queue:
            if entity in self.entities:
                self.entities.remove(entity)
        self.remove_queue.clear()

    def on_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                print("Toggling headless mode")
                self.headless = not self.headless
                return True
            elif event.key == pygame.K_r:
                print("Reseeding")
                self.reseed()
                return True
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
