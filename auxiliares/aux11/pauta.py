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
from auxiliares.utils.helpers import init_axis, init_pipeline, mesh_from_file
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
 

#puntos de control
P = [[-5, 0], [-10, 2.5], [5, 0], [5, 10]]



#funcion bezier
#retorna un punto en la curva definida por los putnos de control
def bezierCurve(t, P0, P1, P2, P3):

    return P0 * pow(1-t, 3) + P1 * 3 * t * pow(1-t, 2) + P2 * 3 * pow(t, 2) * (1-t) + P3 * pow(t, 3)


if __name__ == "__main__":

    #controller/window
    controller = Controller(1000,1000,"Auxiliar 8")
    controller.set_exclusive_mouse(True)

    root = os.path.dirname(__file__)
    #pipeline con un flat shader
    flat_pipeline = init_pipeline(root + "/flat.vert", root + "/flat.frag") 
    #camara
    cam = MyCam([0,2,12])

    shark = mesh_from_file(root + "/shark.obj")[0]['mesh']

    world = SceneGraph(cam)

    # Agrego todos los objetos al grafo

    world.add_node("shark",
                   mesh=shark,
                   pipeline=flat_pipeline,
                   material=Material([0.6, 0.5, 0.9]),
                   rotation=[-np.pi/2, np.pi/2, np.pi],
                   scale=[1.5, 1.5, 1.5]
                   )

    world.add_node("sun",
                   pipeline=flat_pipeline,
                   light=DirectionalLight(ambient=[.6, .6, .6], diffuse=[.6, .6, .6]),
                   rotation=[-np.pi/2, 0, 0]
                   )

    def update(dt):
        

        #Oscila el tiempo entre 0 y 1 
        t = np.sin(controller.time)*0.5 + 0.5

        #Mueve el shark por la curva
        world["shark"]["position"][0] = bezierCurve(
            t, P[0][0], P[1][0], P[2][0], P[3][0])
        world["shark"]["position"][1] = bezierCurve(
            t, P[0][1], P[1][1], P[2][1], P[3][1])

        world.update()
        
        cam.time_update(dt)

        controller.time += dt

    @controller.event
    def on_draw():
        controller.clear()
        glClearColor(0.6, 0.6, 0.9, 1)
        glEnable(GL_DEPTH_TEST)
        
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

    clock.schedule_interval(update, 1/60)
    run()
