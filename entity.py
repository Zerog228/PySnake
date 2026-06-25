import random
import uuid
from enum import Enum

import main


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class EAType(Enum):
    CREATE = 0
    MOVE = 1

class EntityAction:
    def __init__(self, type, **kwargs):
        self.type = type
        self.kwargs = kwargs

class Entity:
    def __init__(self, cords, field_size):
        self.cords = (cords[0] % field_size[0], cords[1] % field_size[1])
        self.field_size = field_size
        self.id = str(uuid.uuid4())
        self.color = "black"

    def tick(self):
        pass

    def rect(self, cell_size):
        return self.cords[0] * cell_size, self.cords[1] * cell_size, cell_size, cell_size

    def add_dir(self, direction):
        self.cords = ((self.cords[0] + direction[0]) % self.field_size[0], (self.cords[1] + direction[1]) % self.field_size[1])
        return self.cords

    def add_neg_dir(self, direction):
        self.cords = ((self.cords[0] + direction[0] * -1) % self.field_size[0], (self.cords[1] + direction[1] * -1) % self.field_size[1])
        return self.cords

class Head(Entity):
    def __init__(self, cords, field_size):
        super().__init__(cords, field_size)
        self.direction = Direction.RIGHT.value
        self.child = None
        self.food = 0
        self.changelist = []
        self.color = "blue"

    def tick(self):
        self.add_dir(self.direction)
        self.changelist.append(EntityAction(EAType.MOVE, id=self.id, location = self.cords, color=self.color))
        if self.child is not None:
            self.child.food += self.food
            self.food = 0
            self.child.tick()
        if self.food > 0:
            self.food -= 1
            self.child = Segment(self, self.cords, self.field_size)
            self.child.add_neg_dir(self.direction)
            self.changelist.append(EntityAction(EAType.CREATE, id=self.child.id, rectangle=self.child.rect(100), color="green"))

            self.child.food = self.food
            self.food = 0

class Segment(Head):
    def __init__(self, parent, cords, field_size):
        super().__init__(cords, field_size)
        self.parent = parent
        self.direction = parent.direction
        self.color = "yellow"

    def tick(self):
        super().tick()
        self.direction = self.parent.direction
        self.parent.changelist.extend(self.changelist)
        self.changelist.clear()

class Apple(Entity):
    def __init__(self, possible_fields, field_size):
        selected = random.choice(possible_fields)

        super().__init__((selected[0] / field_size[0], selected[1] / field_size[1]), field_size)