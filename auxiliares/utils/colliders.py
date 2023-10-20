import numpy as np

class Collider:
    def __init__(self, name):
        self.name = name
        self.type = "undefined"
    
    def set_position(self, position):
        pass

    def detect_collision(self, other):
        return False


class AABB(Collider):
    def __init__(self, name, min, max):
        super().__init__(name)
        self.type = "AABB"
        self.minSize = min
        self.maxSize = max
        self.min = np.array(min)
        self.max = np.array(max)

    def set_position(self, position):
        if (position is None) or (len(position) != 3):
            return
        self.min = np.array(position) + self.minSize
        self.max = np.array(position) + self.maxSize
    
    def detect_collision(self, other):
        if other.type == "AABB":
            return (self.min[0] <= other.max[0] and self.max[0] >= other.min[0]) and \
                   (self.min[1] <= other.max[1] and self.max[1] >= other.min[1]) and \
                   (self.min[2] <= other.max[2] and self.max[2] >= other.min[2])
        if other.type == "Sphere":
            distance = np.linalg.norm(other.center - np.maximum(self.min, np.minimum(other.center, self.max)))
            return distance <= other.radius

        else:
            return False


class Sphere(Collider):
    def __init__(self, name, radius):
        super().__init__(name)
        self.type = "Sphere"
        self.radius = radius
        self.center = np.array([0, 0, 0])

    def set_position(self, position):
        if (position is None) or (len(position) != 3):
            return
        self.center = np.array(position)
    
    def detect_collision(self, other):
        if other.type == "Sphere":
            distance = self.center - other.center
            return distance.dot(distance) <= (self.radius + other.radius) ** 2
        if other.type == "AABB":
            distance = np.linalg.norm(self.center - np.maximum(other.min, np.minimum(self.center, other.max)))
            return distance <= self.radius
            
        else:
            return False


class CollisionManager:
    def __init__(self):
        self.colliders = []

    def add_collider(self, collider):
        self.colliders.append(collider)

    def __getitem__(self, name):
        for c in self.colliders:
            if c.name == name:
                return c
        return None
    
    def set_position(self, name, position):
        collider = self[name]
        if collider is not None:
            collider.set_position(position)

    def check_collision(self, name):
        collider = self[name]
        result = []
        if collider is None:
            return []
        for c in self.colliders:
            # ignorar colisiones de un objeto consigo mismo
            if c.name != collider.name and c.detect_collision(collider):
                result.append(c.name)

        return result