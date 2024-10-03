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
from auxiliares.utils.drawables import Texture, Model, SpotLight, PointLight, DirectionalLight, Material

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

def get_atlas_uv(xoffset, yoffset, atlas):
    dx = 16/atlas.width
    dy = 16/atlas.height
    return [
    dx*xoffset, dy*yoffset,
    dx*(xoffset+1), dy*yoffset,
    dx*(xoffset+1), dy*(yoffset+1),
    dx*xoffset, dy*(yoffset+1) ]

if __name__ == "__main__":

    controller = Controller(800,600,"Auxiliar 7")
    controller.set_exclusive_mouse(True)

    root = os.path.dirname(__file__)
    basic_pipeline = init_pipeline(root + "/basic.vert", root + "/basic.frag")
    light_pipeline = init_pipeline(root + "/textured_mesh_lit.vert", root + "/textured_mesh_lit.frag")
    clight_pipeline = init_pipeline(root + "/color_mesh_lit.vert", root + "/color_mesh_lit.frag")
    lp_list = [light_pipeline, clight_pipeline]
    cam = MyCam([0,2,2])

    # axis = init_axis(cam)


    t_world = SceneGraph(cam)
    world = SceneGraph(cam)
    n_world = SceneGraph(cam)

    floor = Model(shapes.Square["position"], shapes.Square["uv"], shapes.Square["normal"], shapes.Square["indices"])
    world.add_node("floor", mesh=floor, pipeline=clight_pipeline, material=Material(ambient=[0.1, 0.4, 0.0], diffuse=[0.1, 0.4, 0.0], shininess=50), scale=[100, 100, 100], rotation=[-np.pi/2, 0, 0])

    atlas = Texture("assets/atlas.png",minFilterMode=GL_NEAREST, maxFilterMode=GL_NEAREST)

    grass_uv = [
        # cara frontal
        *get_atlas_uv(27,20,atlas),
        # cara trasera
        *get_atlas_uv(27,20,atlas),
        # cara izquierda
        *get_atlas_uv(27,20,atlas),
        # cara derecha
        *get_atlas_uv(27,20,atlas),
        # cara superior
        *get_atlas_uv(28,18,atlas),
        # cara inferior
        *get_atlas_uv(23,23,atlas)]
    g_box = Model(shapes.Cube["position"], grass_uv, shapes.Cube["normal"], index_data=shapes.Cube["indices"])
    world.add_node("grass", mesh=g_box, pipeline=light_pipeline, texture=atlas, position=[-1, 0.5, -1], material=Material(diffuse=[0.8, 0.8, 0.8], specular=[0.1,0.1,0.1], shininess=1))

    gold_uv = [
        # cara frontal
        *get_atlas_uv(27,23,atlas),
        # cara trasera
        *get_atlas_uv(27,23,atlas),
        # cara izquierda
        *get_atlas_uv(27,23,atlas),
        # cara derecha
        *get_atlas_uv(27,23,atlas),
        # cara superior
        *get_atlas_uv(27,23,atlas),
        # cara inferior
        *get_atlas_uv(27,23,atlas)]
    d_box = Model(shapes.Cube["position"], gold_uv, shapes.Cube["normal"], index_data=shapes.Cube["indices"])
    world.add_node("gold", mesh=d_box, pipeline=light_pipeline, texture=atlas, position=[1, .5, -1], material=Material(shininess=100))

    glass_uv = [
        # cara frontal
        *get_atlas_uv(27,28,atlas),
        # cara trasera
        *get_atlas_uv(27,28,atlas),
        # cara izquierda
        *get_atlas_uv(27,28,atlas),
        # cara derecha
        *get_atlas_uv(27,28,atlas),
        # cara superior
        *get_atlas_uv(27,28,atlas),
        # cara inferior
        *get_atlas_uv(27,28,atlas)]

    gl_box = Model(shapes.Cube["position"], glass_uv, shapes.Cube["normal"], index_data=shapes.Cube["indices"])
    t_world.add_node("glass", mesh=gl_box, pipeline=light_pipeline, texture=atlas, position=[0, .5, 0], material=Material())

    glowstone_uv = [
        # cara frontal
        *get_atlas_uv(27,24,atlas),
        # cara trasera
        *get_atlas_uv(27,24,atlas),
        # cara izquierda
        *get_atlas_uv(27,24,atlas),
        # cara derecha
        *get_atlas_uv(27,24,atlas),
        # cara superior
        *get_atlas_uv(27,24,atlas),
        # cara inferior
        *get_atlas_uv(27,24,atlas)]
    glow_box = Model(shapes.Cube["position"], glowstone_uv, shapes.Cube["normal"], index_data=shapes.Cube["indices"])

    world.add_node("sun", light=DirectionalLight(), pipeline=lp_list, rotation=[-np.pi/2, 0, 0])
    world.add_node("cam_light", light=SpotLight(cutOff=0.8, outerCutOff=0.7), pipeline=lp_list)
    world.add_node("lights")
    world.add_node("l0", attach_to="lights", light=PointLight(ambient=[0.05, 0.05, 0.0], diffuse=[0.7, 0.6, 0.1], quadratic=0.00001), pipeline=lp_list, position=[0,3,10])
    world.add_node("l0_model", attach_to="l0", pipeline=basic_pipeline, mesh=glow_box, texture=atlas)

    red_uv = [
        # cara frontal
        *get_atlas_uv(0,7,atlas),
        # cara trasera
        *get_atlas_uv(0,7,atlas),
        # cara izquierda
        *get_atlas_uv(0,7,atlas),
        # cara derecha
        *get_atlas_uv(0,7,atlas),
        # cara superior
        *get_atlas_uv(0,7,atlas),
        # cara inferior
        *get_atlas_uv(0,7,atlas)]
    red_box = Model(shapes.Cube["position"], red_uv, shapes.Cube["normal"], index_data=shapes.Cube["indices"])
    world.add_node("l1", attach_to="lights", light=PointLight(ambient=[0.1, 0.0, 0.0], diffuse=[0.8, 0.1, 0.1], specular=[1.0, 0.2, 0.2], quadratic=0.01), pipeline=lp_list, position=[0,3,-10])
    world.add_node("l1_model", attach_to="l1", pipeline=basic_pipeline, mesh=red_box, texture=atlas)


    @controller.event
    def on_draw():
        controller.clear()
        glClearColor(*(controller.sky_color * controller.intensity),1)
        glEnable(GL_DEPTH_TEST)
        # pueden cambiar el orden de visualización y ver que pasa
        n_world.draw()
        world.draw()
        glEnable( GL_BLEND )
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        t_world.draw()
        glDisable( GL_BLEND )

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
        t_world.update()
        # axis.update()
        cam.time_update(dt)
            # world["light"]["position"] = cam.position + cam.forward*controller.light_distance
        # controller.sun_time += dt*0.5
        if controller.light_mode:
            world["cam_light"]["light"].ambient = [0,0,0]
            world["cam_light"]["light"].diffuse = [0.0,0.4,1.0]
            world["cam_light"]["light"].specular = [1.0,1.0,1.0]
        else:
            world["cam_light"]["light"].ambient = [0,0,0]
            world["cam_light"]["light"].diffuse = [0,0,0]
            world["cam_light"]["light"].specular = [0,0,0]

        world["cam_light"]["position"] = cam.position
        world["cam_light"]["rotation"] = [cam.pitch, -cam.yaw - np.pi/2, 0]
        world["sun"]["rotation"][2] = np.interp(controller.time, [0.0, 10.0], [-np.pi/2, np.pi/2], period=10)
        controller.intensity = np.interp(controller.time, [0.0, 1.0, 9.0, 10.0], [0.0, 1.0, 1.0, 0.0], period=20)
        world["sun"]["light"].diffuse = [controller.intensity] * 3
        world["sun"]["light"].specular = [controller.intensity] * 3
        world["lights"]["rotation"][1] = controller.time

        world.update()

        controller.time += dt

    clock.schedule_interval(update,1/60)
    run()

