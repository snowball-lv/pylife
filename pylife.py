# Example file showing a basic pygame "game loop"
import pygame
import random
import pygame.math

# pygame setup
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
running = True

actors = []
new_generation = []

class Genome:

    def __init__(self):
        self.genes = [0.0] * 100
        for i in range(len(self.genes)):
            self.genes[i] = random.random() * 2.0 - 1.0
    
    def get_feature(self, name):
        pos = hash(name) % len(self.genes)
        return self.genes[pos]

    def mix(self, other):
        pass

class Actor:

    def __init__(self):
        self.genome = Genome()
        x = random.randrange(0, 800)
        y = random.randrange(0, 600)
        self.pos = pygame.Vector2(x, y)
        self.size = pygame.Vector2(8, 8)
        self.age = 0.0
        # cached features
        velocity_x = self.genome.get_feature("velocity_x")
        velocity_y = self.genome.get_feature("velocity_y")
        self.velocity = pygame.Vector2(velocity_x, velocity_y)

    def multiply(self, other):
        pass

    def update(self, delta):
        # update position
        pos = self.pos + self.velocity * delta * 50
        if pos.x < 0 or pos.x >= 800:
            self.velocity.x *= -1
        if pos.y < 0 or pos.y >= 600:
            self.velocity.y *= -1
        self.pos = pos
        # multiply
        for other in actors:
            if self is other:
                continue
            

    def draw(self):
        green = pygame.Color("green")
        red = pygame.Color("red")
        longevity = self.genome.get_feature("longevity")
        color = green.lerp(red, self.age / longevity)
        pygame.draw.rect(screen, color, pygame.Rect(self.pos - self.size / 2, self.size))

for i in range(10):
    actors.append(Actor())

while running:

    delta = clock.tick(60) / 1000.0  # limits FPS to 60

    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("ivory")

    # RENDER YOUR GAME HERE
    for actor in actors:
        actor.update(delta)

    for actor in actors:
        actor.draw()

    actors = actors + new_generation
    new_generation = []

    # flip() the display to put your work on screen
    pygame.display.flip()


pygame.quit()
