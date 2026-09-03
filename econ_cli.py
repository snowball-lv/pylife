import time

class Actor:

    ID_COUNTER = 1

    def get_next_id():
        id = Actor.ID_COUNTER
        Actor.ID_COUNTER += 1
        return id

    def __init__(self):
        self.id = Actor.get_next_id()
        self.food = 10

    def print(self, text):
        print("Actor {}: {}".format(self.id, text))

class Sim:

    def __init__(self):
        self.ticks = 0
        self.actors = []
        self.remove = []
        for i in range(10):
            self.actors.append(Actor())

    def buy_food(self, actor):
        actor.print("buying food")

    def update_actor(self, actor):
        actor.food -= 1
        if actor.food < 5:
            self.buy_food(actor)
        if actor.food <= 0:
            actor.print("out of food")
            self.remove.append(actor)

    def tick(self):
        print("Tick {}".format(self.ticks))
        for actor in self.actors:
            self.update_actor(actor)
        for actor in self.remove:
            self.actors.remove(actor)
        self.remove = []
        self.ticks += 1
        time.sleep(1.0)

    def run(self):
        while len(self.actors) > 0:
            self.tick()


def main():
    sim = Sim()
    sim.run()

if __name__ == "__main__":
    main()
