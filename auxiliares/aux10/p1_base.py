from ctypes.wintypes import SIZE
from numpy._core.fromnumeric import sort
from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.window import Window, key
from pyglet.gl import *
from pyglet.app import run
from pyglet import math
from pyglet import clock

import sys, os
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))
from auxiliares.utils.helpers import init_axis, mesh_from_file, init_pipeline
from auxiliares.utils.camera import FreeCamera
from auxiliares.utils.scene_graph import SceneGraph
from auxiliares.utils import shapes
from auxiliares.utils.drawables import (
    Texture,
    Model,
    SpotLight,
    PointLight,
    DirectionalLight,
    Material,
)

from auxiliares.utils import colliders


class Controller(Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class MyCam(FreeCamera):
    def __init__(self, position=np.array([0, 0, 0]), camera_type="perspective"):
        super().__init__(position, camera_type)
        self.direction = np.zeros(3)
        self.velocity = np.zeros(3)
        self.speed = 5

    def physics_update(self, dt):
        self.update()
        dir = self.direction[2] * self.forward + self.direction[0] * self.right
        dir_norm = np.linalg.norm(dir)
        if dir_norm:
            dir /= dir_norm
        self.velocity += dir * self.speed
        self.position += self.velocity * dt
        self.velocity = np.zeros(3)
        self.focus = self.position + self.forward



def get_atlas_uv(xoffset, yoffset, atlas):
    dx = 16 / atlas.width
    dy = 16 / atlas.height
    return [
        dx * xoffset,
        dy * yoffset,
        dx * (xoffset + 1),
        dy * yoffset,
        dx * (xoffset + 1),
        dy * (yoffset + 1),
        dx * xoffset,
        dy * (yoffset + 1),
    ]




class MyChunk(Model):
    SIZE = 16
    COUNT = 16

    def __init__(self, id, atlas):
        super().__init__([], [], [], [])
        self.index_data = []
        self.atlas = atlas
        self.id = id

    def init_gpu_data(self, pipeline):
        delta = MyChunk.SIZE / MyChunk.COUNT
        cube_positions = [(coord + 0.5) * delta for coord in shapes.Cube["position"]]
        cube_positions = np.reshape(cube_positions, (len(cube_positions) // 3, 3))
        deltaV = cube_positions.shape[0]
        vcount = 0

        super().init_gpu_data(pipeline)



if __name__ == "__main__":

    controller = Controller(1280, 720, "Auxiliar 10")
    controller.set_exclusive_mouse(True)

    shaders_folder = os.path.join(os.path.dirname(__file__), "shaders")
    pipeline = init_pipeline(
        shaders_folder + "/phong.vert", shaders_folder + "/phong.frag"
    )

    cam = MyCam([0.5, 2, 0.5])

    world = SceneGraph(cam)
    outline_world = SceneGraph(cam)

    atlas = Texture(
        "assets/atlas.png", minFilterMode=GL_NEAREST, maxFilterMode=GL_NEAREST
    )


    world.add_node(
        "sun",
        light=DirectionalLight(ambient=[0.2, 0.2, 0.2]),
        pipeline=pipeline,
        rotation=[-np.pi / 4, -np.pi / 4, 0],
    )

    @controller.event
    def on_draw():
        controller.clear()
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)
        # pueden cambiar el orden de visualización y ver que pasa
        world.draw()

    @controller.event
    def on_key_press(symbol, modifiers):
        if symbol == key.W:
            cam.direction[2] = 1
        if symbol == key.S:
            cam.direction[2] = -1

        if symbol == key.A:
            cam.direction[0] = 1
        if symbol == key.D:
            cam.direction[0] = -1

    @controller.event
    def on_key_release(symbol, modifiers):
        if symbol == key.W or symbol == key.S:
            cam.direction[2] = 0

        if symbol == key.A or symbol == key.D:
            cam.direction[0] = 0

    @controller.event
    def on_mouse_motion(x, y, dx, dy):
        cam.yaw += dx * 0.001
        cam.pitch += dy * 0.001
        cam.pitch = math.clamp(cam.pitch, -(np.pi / 2 - 0.01), np.pi / 2 - 0.01)

    def update(dt):
        print(f"FPS: {1/dt}")
        world.update()
        cam.physics_update(dt)

    clock.schedule_interval(update, 1 / 60)
    run()
