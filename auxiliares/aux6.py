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

import grafica.transformations as tr
import auxiliares.utils.shapes as shapes
from auxiliares.utils.camera import FreeCamera
from auxiliares.utils.scene_graph import SceneGraph
from auxiliares.utils.drawables import Model, Texture, DirectionalLight
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
        self.program_state = { "total_time": 0.0, "camera": None, "light": None }
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
    controller = Controller("Auxiliar 6", width=WIDTH, height=HEIGHT, resizable=True)

    controller.program_state["camera"] = FreeCamera([1, 2, 2], "perspective")
    controller.program_state["camera"].yaw = -3* np.pi/ 4
    controller.program_state["camera"].pitch = -np.pi / 4

    controller.program_state["light"] = DirectionalLight()
    
    axis_scene = init_axis(controller)

    color_mesh_pipeline = init_pipeline(
        get_path("auxiliares/shaders/color_mesh.vert"),
        get_path("auxiliares/shaders/color_mesh.frag"))
    
    textured_mesh_pipeline = init_pipeline(
        get_path("auxiliares/shaders/textured_mesh.vert"),
        get_path("auxiliares/shaders/textured_mesh.frag"))
    
    lit_textured_mesh_pipeline = init_pipeline(
        get_path("auxiliares/shaders/textured_mesh_lit.vert"),
        get_path("auxiliares/shaders/textured_mesh_lit.frag"))

    cube = Model(shapes.Cube["position"], shapes.Cube["uv"], shapes.Cube["normal"], index_data=shapes.Cube["indices"])
    pyramid = Model(shapes.SquarePyramid["position"], shapes.SquarePyramid["uv"], shapes.SquarePyramid["normal"], index_data=shapes.SquarePyramid["indices"])
    triangle = Model(shapes.Triangle["position"], shapes.Triangle["uv"], shapes.Triangle["normal"])
    quad = Model(shapes.Square["position"], shapes.Square["uv"], shapes.Square["normal"], index_data=shapes.Square["indices"])

    textura = Texture("assets/bricks.jpg")
    textura2 = Texture("assets/boo.png", maxFilterMode=GL.GL_NEAREST)

    graph = SceneGraph(controller)
    graph.add_node("shapes")

    # mesh_from_file() devuelve una lista de diccionarios, cada uno con la información de un mesh
    # [{id, mesh, texture}, ...]
    zorzal = mesh_from_file("assets/zorzal.obj")
    for i in range(len(zorzal)):
        graph.add_node(zorzal[i]["id"],
                    attach_to="root",
                    mesh=zorzal[i]["mesh"],
                    pipeline=textured_mesh_pipeline,
                    texture=zorzal[i]["texture"],
                    cull_face=False)

    graph.add_node("cube",
                   attach_to="shapes",
                   mesh = cube,
                   pipeline = lit_textured_mesh_pipeline,
                   texture = textura,
                   position = [-2, 0, 0],
                   color = [1, 0, 0])
    graph.add_node("pyramid",
                     attach_to="shapes",
                     mesh = pyramid,
                     pipeline = lit_textured_mesh_pipeline,
                     texture=Texture(), # Textura vacía
                     position = [2, 0, 0],
                     color = [0, 1, 0])
    graph.add_node("triangle",
                    attach_to="shapes",
                    mesh = triangle,
                    pipeline = color_mesh_pipeline,
                    position = [0, 0, 2],
                    color = [0, 0, 1])
    graph.add_node("quad",
                    attach_to="shapes",
                    mesh = quad,
                    pipeline = textured_mesh_pipeline,
                    texture = textura2,
                    position = [0, 0, -2],
                    color = [1, 1, 1])
    
    def update(dt):
        controller.program_state["total_time"] += dt
        camera = controller.program_state["camera"]
        light = controller.program_state["light"]
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
            light.rotateX(-dt)
        if controller.is_key_pressed(pyglet.window.key.DOWN):
            light.rotateX(dt)
        if controller.is_key_pressed(pyglet.window.key.LEFT):
            light.rotateY(-dt)
        if controller.is_key_pressed(pyglet.window.key.RIGHT):
            light.rotateY(dt)

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


    # draw loop
    @controller.event
    def on_draw():
        controller.clear()
        axis_scene.draw()
        graph.draw()

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()
