import numpy as np
import grafica.transformations as tr

WIDTH = 640
HEIGHT = 640

class Camera():
    def __init__(self, camera_type = "perspective", width = WIDTH, height = HEIGHT):
        self.position = np.array([1, 0, 0], dtype=np.float32)
        self.focus = np.array([0, 0, 0], dtype=np.float32)
        self.type = camera_type
        self.width = width
        self.height = height

    def update(self):
        pass

    def get_view(self):
        lookAt_matrix = tr.lookAt(self.position, self.focus, np.array([0, 1, 0], dtype=np.float32))
        return np.reshape(lookAt_matrix, (16, 1), order="F")

    def get_projection(self):
        perspective_matrix = tr.identity()
        if self.type == "perspective":
            perspective_matrix = tr.perspective(90, self.width / self.height, 0.01, 100)
        elif self.type == "orthographic":
            depth = self.position - self.focus
            depth = np.linalg.norm(depth)
            perspective_matrix = tr.ortho(-(self.width/self.height) * depth, (self.width/self.height) * depth, -1 * depth, 1 * depth, 0.01, 100)
        return np.reshape(perspective_matrix, (16, 1), order="F")
    
    def resize(self, width, height):
        self.width = width
        self.height = height

class OrbitCamera(Camera):
    def __init__(self, distance, camera_type = "perspective"):
        super().__init__(camera_type)
        self.distance = distance
        self.phi = 0
        self.theta = np.pi / 2
        self.update()

    def update(self):
        if self.theta > np.pi:
            self.theta = np.pi
        elif self.theta < 0:
            self.theta = 0.0001

        self.position[0] = self.distance * np.sin(self.theta) * np.sin(self.phi)
        self.position[1] = self.distance * np.cos(self.theta)
        self.position[2] = self.distance * np.sin(self.theta) * np.cos(self.phi)

class FreeCamera(Camera):
    def __init__(self, position = [0, 0, 0], camera_type = "perspective"):
        super().__init__(camera_type)
        self.position = np.array(position, dtype=np.float32)
        self.pitch = 0
        self.yaw = 0
        self.forward = np.array([0, 0, -1], dtype=np.float32)
        self.right = np.array([1, 0, 0], dtype=np.float32)
        self.up = np.array([0, 1, 0], dtype=np.float32)
        self.update()
    
    def update(self):
        self.forward[0] = np.cos(self.yaw) * np.cos(self.pitch)
        self.forward[1] = np.sin(self.pitch)
        self.forward[2] = np.sin(self.yaw) * np.cos(self.pitch)
        self.forward = self.forward / np.linalg.norm(self.forward)

        self.right = np.cross(np.array([0, 1, 0], dtype=np.float32), self.forward)
        self.right = self.right / np.linalg.norm(self.right)

        self.up = np.cross(self.right, self.forward)
        self.up = self.up / np.linalg.norm(self.up)

        self.focus = self.position + self.forward
