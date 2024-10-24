from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.window import Window, key
from pyglet.gl import *
from pyglet.app import run
from pyglet import math
from pyglet import clock
import sys, os
import numpy as np
import trimesh as tm

sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))
from auxiliares.utils.helpers import init_axis, init_pipeline
from auxiliares.utils.camera import FreeCamera
from auxiliares.utils.scene_graph import SceneGraph
from auxiliares.utils.drawables import Model, DirectionalLight, Material

class Controller(Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.time = 0
        self.sky_color = np.array([0.2, 0.3, 0.5])
        self.intensity = 0.1
        self.light_mode = False
        self.light_dir = np.zeros(2)
        self.light_color = np.ones(3)
        self.light_distance = 1

class MyCam(FreeCamera):
    def __init__(self, position=np.array([0, 0, 0]), camera_type="perspective"):
        super().__init__(position, camera_type)
        self.direction = np.array([0,0,0])
        self.speed = 2

    def time_update(self, dt):
        self.update()
        dir = self.direction[0]*self.forward + self.direction[1]*self.right
        dir_norm = np.linalg.norm(dir)
        if dir_norm:
            dir /= dir_norm
        self.position += dir*self.speed*dt
        self.focus = self.position + self.forward


if __name__ == "__main__":

    #controller/window
    controller = Controller(1000,1000,"Auxiliar 8")
    controller.set_exclusive_mouse(True)

    root = os.path.dirname(__file__)
    #pipeline con un flat shader
    flat_pipeline = init_pipeline(root + "/flat.vert", root + "/flat.frag") 
    #camara
    cam = MyCam([0,1,0])
    #axis para mayor claridad
    axis = init_axis(cam)

    world = SceneGraph(cam)

    n = 50

    vertices = []

    normals = []

    #generar vertices y normales
    for i in range(n):
        for j in range(n):

            vertices += [j, 0, i]
            normals += [0, 1, 0]

    #generar indices
    #son dos triangulos por cuadrado
    indices = []
    for i in range(n-1):
        for j in range(n-1):
            indices += [n*(i+1) + j + 1, n*i + j + 1, n * i + j]
            indices += [n*(i+1) + j, n*(i+1) + j + 1, n * i + j]

    #hacer ruido random
    for i in range(n*n):

        vertices[np.random.randint(0, n*n) * 3 + 1] += 0.5
    
    #hacemos el mesh como siempre
    mesh = Model(vertices, normal_data=normals, index_data=indices)

    #agregamos a la escena
    world.add_node("mesh", mesh=mesh, mode=GL_TRIANGLES, pipeline=flat_pipeline, position=[0, 0, 0], scale=[0.2, 0.2, 0.2], material=Material(ambient=[0.8, 0.5, 0.5], diffuse=[0.8, .5, .5]))

    #agregamos una luz
    world.add_node("dirLight", light=DirectionalLight(ambient=[.6, .6, .6], diffuse=[.6, .6, .6]), pipeline=flat_pipeline, rotation=[-np.pi/4, 0, 0])

    @controller.event
    def on_draw():
        controller.clear()
        glClearColor(*(controller.sky_color * controller.intensity),1)
        glEnable(GL_DEPTH_TEST)
        # pueden cambiar el orden de visualización y ver que pasa
        
        axis.draw()
        world.draw()

    @controller.event
    def on_key_press(symbol, modifiers):
        if symbol == key.SPACE: controller.light_mode = not controller.light_mode
        if symbol == key.W:
            cam.direction[0] = 1
        if symbol == key.S:
            cam.direction[0] = -1

        if symbol == key.A:
            cam.direction[1] = 1
        if symbol == key.D:
            cam.direction[1] = -1


    @controller.event
    def on_key_release(symbol, modifiers):
        if symbol == key.W or symbol == key.S:
            cam.direction[0] = 0

        if symbol == key.A or symbol == key.D:
            cam.direction[1] = 0

    @controller.event
    def on_mouse_motion(x, y, dx, dy):
        cam.yaw += dx * .001
        cam.pitch += dy * .001
        cam.pitch = math.clamp(cam.pitch, -(np.pi/2 - 0.01), np.pi/2 - 0.01)

    @controller.event
    def on_mouse_scroll(x, y, scroll_x, scroll_y):
        controller.light_distance += scroll_y*.01

    def update(dt):
        world.update()
        axis.update()
        cam.time_update(dt)

        world.update()
        axis.update()

        controller.time += dt

    clock.schedule_interval(update,1/60)
    run()

