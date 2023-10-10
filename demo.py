import pyglet
from OpenGL import GL
import numpy as np
import sys

# No es necesario este bloque de código si se ejecuta desde la carpeta raíz del repositorio
# v
if sys.path[0] != "":
    sys.path.insert(0, "")
sys.path.append('../../')
# ^
# No es necesario este bloque de código si se ejecuta desde la carpeta raíz del repositorio

import auxiliares.utils.shapes as shapes
from auxiliares.utils.camera import FreeCamera
from auxiliares.utils.scene_graph import SceneGraph
from auxiliares.utils.drawables import Model, Texture, DirectionalLight, PointLight, SpotLight, Material
from auxiliares.utils.helpers import init_axis, init_pipeline, mesh_from_file, get_path

WIDTH = 640
HEIGHT = 640

class Controller(pyglet.window.Window):
    def __init__(self, title, *args, **kargs):
        super().__init__(*args, **kargs)
        self.set_minimum_size(240, 240) # Evita error cuando se redimensiona a 0
        self.set_caption(title)
        self.key_handler = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.key_handler)
        self.program_state = { "total_time": 0.0, "camera": None }
        self.init()

    def init(self):
        GL.glClearColor(1, 1, 1, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        GL.glFrontFace(GL.GL_CCW)

    def is_key_pressed(self, key):
        return self.key_handler[key]

if __name__ == "__main__":
    # Instancia del controller
    controller = Controller("Demo", width=WIDTH, height=HEIGHT, resizable=True)

    controller.program_state["camera"] = FreeCamera([1, 2, 2], "perspective")
    controller.program_state["camera"].yaw = -3* np.pi/ 4
    controller.program_state["camera"].pitch = -np.pi / 4
    
    axis_scene = init_axis(controller)

    color_mesh_pipeline = init_pipeline(
        get_path("auxiliares/shaders/color_mesh.vert"),
        get_path("auxiliares/shaders/color_mesh.frag"))
    
    textured_mesh_pipeline = init_pipeline(
        get_path("auxiliares/shaders/textured_mesh.vert"),
        get_path("auxiliares/shaders/textured_mesh.frag"))
    
    textured_mesh_lit_pipeline = init_pipeline(
        get_path("auxiliares/shaders/textured_mesh_lit.vert"),
        get_path("auxiliares/shaders/textured_mesh_lit.frag"))

    cube = Model(shapes.Cube["position"], shapes.Cube["uv"], shapes.Cube["normal"], index_data=shapes.Cube["indices"])
    pyramid = Model(shapes.SquarePyramid["position"], shapes.SquarePyramid["uv"], shapes.SquarePyramid["normal"], index_data=shapes.SquarePyramid["indices"])
    triangle = Model(shapes.Triangle["position"], shapes.Triangle["uv"], shapes.Triangle["normal"])
    quad = Model(shapes.Square["position"], shapes.Square["uv"], shapes.Square["normal"], index_data=shapes.Square["indices"])
    arrow = mesh_from_file("assets/arrow.off")[0]["mesh"]

    bricks = Texture("assets/bricks.jpg")
    wall2 = Texture("assets/wall2.jpg")
    boo = Texture("assets/boo.png", maxFilterMode=GL.GL_NEAREST)

    graph = SceneGraph(controller)

    graph.add_node("sun",
                   pipeline=textured_mesh_lit_pipeline,
                   position=[0, 2, 0],
                   light=DirectionalLight(diffuse = [0.5, 0.5, 0.5], specular = [0.5, 0.25, 0.5], ambient = [0.15, 0.15, 0.15]))
    graph.add_node("sun_arrow",
                   attach_to="sun",
                   mesh=arrow,
                   position=[0, 0, -0.5],
                   rotation=[-np.pi, 0, 0],
                   scale=[0.5, 0.5, 0.5],
                   color=[1,1,0],
                   pipeline=color_mesh_pipeline)
    
    graph.add_node("point_lights")
    graph.add_node("point_light1",
                    attach_to="point_lights",
                    pipeline=textured_mesh_lit_pipeline,
                    position=[8, 1, 8],
                    light=PointLight(diffuse = [0, 0, 1], specular = [1, 1, 0], ambient = [0.1, 0.1, 0.1]))
    
    graph.add_node("point_light2",
                    attach_to="point_lights",
                    pipeline=textured_mesh_lit_pipeline,
                    position=[-8, 1, -8],
                    light=PointLight(diffuse = [0, 1, 0], specular = [1, 0, 1], ambient = [0.1, 0.1, 0.1]))
    
    graph.add_node("point_light3",
                    attach_to="point_lights",
                    pipeline=textured_mesh_lit_pipeline,
                    position=[-8, 1, 8],
                    light=PointLight(diffuse = [1, 0, 0], specular = [0, 1, 1], ambient = [0.1, 0.1, 0.1]))
    
    graph.add_node("spotlight",
                    pipeline=textured_mesh_lit_pipeline,
                    position=[0, 3, 0],
                    rotation=[np.pi/4, 0, 0],
                    light=SpotLight(diffuse = [1, 1, 1],
                          specular = [0, 1, 0],
                          ambient = [0.1, 0.1, 0.1]))


    graph.add_node("shapes")

    # mesh_from_file() devuelve una lista de diccionarios, cada uno con la información de un mesh
    # [{id, mesh, texture}, ...]
    zorzal = mesh_from_file("assets/zorzal.obj")
    for i in range(len(zorzal)):
        graph.add_node(zorzal[i]["id"],
                    attach_to="root",
                    mesh=zorzal[i]["mesh"],
                    pipeline=textured_mesh_lit_pipeline,
                    material=Material(),
                    texture=zorzal[i]["texture"],
                    cull_face=False)

    graph.add_node("cube",
                   attach_to="shapes",
                   mesh = cube,
                   pipeline = textured_mesh_lit_pipeline,
                   texture = bricks,
                   position = [-2, 0, 0],
                   material = Material(
                          diffuse = [1, 0, 0],
                          specular = [1, 0, 1],
                          ambient = [0.1, 0, 0],
                          shininess = 128
                     ))
    graph.add_node("pyramid",
                     attach_to="shapes",
                     mesh = pyramid,
                     pipeline = textured_mesh_lit_pipeline,
                     position = [2, 0, 0],
                     material = Material(
                          diffuse = [0, 0, 1],
                          specular = [0, 1, 0],
                          ambient = [0.1, 0, 0],
                          shininess = 32
                     ))
    graph.add_node("boo",
                    attach_to="shapes",
                    mesh = quad,
                    pipeline = textured_mesh_pipeline,                    
                    position = [0, 0, -2],
                    texture = boo,
                    color = [0, 0, 1])
    graph.add_node("floor",
                    attach_to="shapes",
                    mesh = quad,
                    pipeline = textured_mesh_lit_pipeline,
                    position = [0, -1, 0],
                    rotation = [-np.pi/2, 0, 0],
                    scale = [20, 20, 20],
                    texture=wall2,
                    material = Material(
                          diffuse = [1, 1, 1],
                          specular = [0.5, 0.5, 0.5],
                          ambient = [0.1, 0.1, 0.1],
                          shininess = 256
                     ))
    
    def update(dt):
        controller.program_state["total_time"] += dt
        camera = controller.program_state["camera"]
        sun = graph["sun"]
        if controller.is_key_pressed(pyglet.window.key.A):
            camera.position -= camera.right * dt
        if controller.is_key_pressed(pyglet.window.key.D):
            camera.position += camera.right * dt
        if controller.is_key_pressed(pyglet.window.key.W):
            camera.position += camera.forward * dt
        if controller.is_key_pressed(pyglet.window.key.S):
            camera.position -= camera.forward * dt
        if controller.is_key_pressed(pyglet.window.key.Q):
            camera.position[1] -= dt
        if controller.is_key_pressed(pyglet.window.key.E):
            camera.position[1] += dt
        if controller.is_key_pressed(pyglet.window.key._1):
            camera.type = "perspective"
        if controller.is_key_pressed(pyglet.window.key._2):
            camera.type = "orthographic"
        camera.update()

        if controller.is_key_pressed(pyglet.window.key.UP):
            sun["rotation"][0] -= 2 * dt
        if controller.is_key_pressed(pyglet.window.key.DOWN):
            sun["rotation"][0] += 2 * dt
        if controller.is_key_pressed(pyglet.window.key.LEFT):
            sun["rotation"][1] -= 2 * dt
        if controller.is_key_pressed(pyglet.window.key.RIGHT):
            sun["rotation"][1] += 2 * dt

        graph["point_lights"]["rotation"][1] += 2 * dt

    @controller.event
    def on_resize(width, height):
        controller.program_state["camera"].resize(width, height)

    @controller.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        if buttons & pyglet.window.mouse.RIGHT:
            controller.program_state["camera"].yaw += dx * 0.01
            controller.program_state["camera"].pitch += dy * 0.01
        
        if buttons & pyglet.window.mouse.LEFT:
            graph["root"]["rotation"][0] += dy * 0.01
            graph["root"]["rotation"][1] += dx * 0.01

        if buttons & pyglet.window.mouse.MIDDLE:
            graph["spotlight"]["rotation"][0] += dy * 0.01
            graph["spotlight"]["rotation"][1] += dx * 0.01


    # draw loop
    @controller.event
    def on_draw():
        controller.clear()
        axis_scene.draw()
        graph.draw()

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()
