import numpy as np


class Collider:
    def __init__(self, name):
        self.name = name

    def set_position(self, position):
        pass

    def detect_collision(self, other):
        return False

    def detect_collision_with_aabb(self, aabb):
        return False

    def detect_collision_with_sphere(self, sphere):
        return False


class AABB(Collider):
    def __init__(self, name, min, max):
        super().__init__(name)
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
        return other.detect_collision_with_aabb(self)

    def detect_collision_with_aabb(self, aabb):
        return (
            (self.min[0] <= aabb.max[0] and self.max[0] >= aabb.min[0])
            and (self.min[1] <= aabb.max[1] and self.max[1] >= aabb.min[1])
            and (self.min[2] <= aabb.max[2] and self.max[2] >= aabb.min[2])
        )

    def detect_collision_with_sphere(self, sphere):
        distance = np.linalg.norm(
            sphere.center - np.maximum(self.min, np.minimum(sphere.center, self.max))
        )
        return distance <= sphere.radius


class Sphere(Collider):
    def __init__(self, name, radius):
        super().__init__(name)
        self.radius = radius
        self.center = np.array([0, 0, 0])

    def set_position(self, position):
        if (position is None) or (len(position) != 3):
            return
        self.center = np.array(position)

    def detect_collision(self, other):
        return other.detect_collision_with_sphere(self)

    def detect_collision_with_aabb(self, aabb):
        distance = np.linalg.norm(
            self.center - np.maximum(aabb.min, np.minimum(self.center, aabb.max))
        )
        return distance <= self.radius

    def detect_collision_with_sphere(self, sphere):
        distance = self.center - sphere.center
        return distance.dot(distance) <= (self.radius + sphere.radius) ** 2


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

