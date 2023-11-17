import pyglet
from OpenGL import GL
import numpy as np
import sys
from Box2D import b2World

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
from auxiliares.utils.drawables import Model, DirectionalLight, Material
from auxiliares.utils.helpers import init_axis, init_pipeline, get_path

WIDTH = 1280
HEIGHT = 720

class Controller(pyglet.window.Window):
    def __init__(self, title, *args, **kargs):
        super().__init__(*args, **kargs)
        self.set_minimum_size(240, 240) # Evita error cuando se redimensiona a 0
        self.set_caption(title)
        self.keys_state = {}
        self.program_state = {
            "total_time": 0.0,
            "camera": None,
            "bodies": {},
            "world": None,
            # parámetros para el integrador
            "vel_iters": 6,
            "pos_iters": 2 }
        self.init()

    def init(self):
        GL.glClearColor(1, 1, 1, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        GL.glFrontFace(GL.GL_CCW)

    def is_key_pressed(self, key):
        return self.keys_state.get(key, False)

    def on_key_press(self, symbol, modifiers):
        controller.keys_state[symbol] = True
        super().on_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        controller.keys_state[symbol] = False


if __name__ == "__main__":
    # Instancia del controller
    controller = Controller("Auxiliar 9", width=WIDTH, height=HEIGHT, resizable=True)

    controller.program_state["camera"] = FreeCamera([0, 4, 3], "perspective")
    controller.program_state["camera"].yaw = -np.pi/ 2
    controller.program_state["camera"].pitch = -np.pi / 2.5

    color_mesh_lit_pipeline = init_pipeline(
        get_path("auxiliares/shaders/color_mesh_lit.vert"),
        get_path("auxiliares/shaders/color_mesh_lit.frag"))
    
    axis_scene = init_axis(controller)

    cube = Model(shapes.Cube["position"], shapes.Cube["uv"], shapes.Cube["normal"], index_data=shapes.Cube["indices"])
    quad = Model(shapes.Square["position"], shapes.Square["uv"], shapes.Square["normal"], index_data=shapes.Square["indices"])

    graph = SceneGraph(controller)
    graph.add_node("sun",
                   pipeline=color_mesh_lit_pipeline,
                   position=[0, 2, 0],
                   rotation=[-3*np.pi/4, 0, 0],
                   light=DirectionalLight(diffuse = [1, 1, 1], specular = [0.25, 0.25, 0.25], ambient = [0.15, 0.15, 0.15]))

    graph.add_node("floor",
                    mesh = quad,
                    pipeline = color_mesh_lit_pipeline,
                    position = [0, -1, 0],
                    rotation = [-np.pi/2, 0, 0],
                    scale = [10, 10, 10],
                    material = Material(
                          diffuse = [1, 1, 1],
                          specular = [0.5, 0.5, 0.5],
                          ambient = [0.1, 0.1, 0.1],
                          shininess = 256
                     ))
    
    graph.add_node("locomotive",
                    mesh = cube,
                    pipeline = color_mesh_lit_pipeline,
                    position = [0, 0, 0],
                    scale = [0.5, 0.5, 1],
                    material = Material(diffuse = [1, 0, 0]))
    
    graph.add_node("wagon",
                    mesh = cube,
                    pipeline = color_mesh_lit_pipeline,
                    scale = [0.5, 0.5, 0.5],
                    material = Material(diffuse = [0, 1, 0]))
    
    world = b2World(gravity=(0, 0))
    controller.program_state["world"] = world

    locomotive = world.CreateDynamicBody(position=(0, 0), angle=0, linearDamping=0.75, angularDamping=0.5)
    locomotive.CreatePolygonFixture(box=(0.25, 0.5), density=4, friction=0.3)
    controller.program_state["bodies"]["locomotive"] = locomotive

    wagon = world.CreateDynamicBody(position=(0, -1), angle=0, linearDamping=0.5, angularDamping=0.5)
    wagon.CreatePolygonFixture(box=(0.25, 0.25), density=1, friction=0.3)
    controller.program_state["bodies"]["wagon"] = wagon

    world.CreateRevoluteJoint(bodyA=locomotive, bodyB=wagon, anchor=(0, -0.5), collideConnected=True)

    def update_world(dt):
        controller.program_state["total_time"] += dt
        controller.program_state["world"].Step(dt, controller.program_state["vel_iters"], controller.program_state["pos_iters"])

        graph["locomotive"]["position"][0] = locomotive.position[0]
        graph["locomotive"]["position"][2] = locomotive.position[1]
        graph["locomotive"]["rotation"][1] = -locomotive.angle

        graph["wagon"]["position"][0] = wagon.position[0]
        graph["wagon"]["position"][2] = wagon.position[1]
        graph["wagon"]["rotation"][1] = -wagon.angle

        

    def update(dt):
        update_world(dt)
        camera = controller.program_state["camera"]

        #controllable = graph["locomotive"]
        controllable = controller.program_state["bodies"]["locomotive"]

        if controller.is_key_pressed(pyglet.window.key.W):
            forward = graph.get_forward("locomotive")
            #controllable["position"][0] += graph.get_forward("locomotive")[0] * 2*dt
            #controllable["position"][2] += graph.get_forward("locomotive")[2] * 2*dt
            locomotive.ApplyForceToCenter((forward[0]*10, forward[2]*10), True)


        if controller.is_key_pressed(pyglet.window.key.S):
            forward = graph.get_forward("locomotive")
            #controllable["position"][0] -= graph.get_forward("locomotive")[0] * 2*dt
            #controllable["position"][2] -= graph.get_forward("locomotive")[2] * 2*dt
            locomotive.ApplyForceToCenter((-forward[0]*10, -forward[2]*10), True)

        if controller.is_key_pressed(pyglet.window.key.D):
            #controllable["rotation"][1] -= 2*dt
            locomotive.angularVelocity = 1
        if controller.is_key_pressed(pyglet.window.key.A):
            #controllable["rotation"][1] += 2*dt
            locomotive.angularVelocity = -1
        
        if controller.is_key_pressed(pyglet.window.key._1):
            camera.type = "perspective"
        if controller.is_key_pressed(pyglet.window.key._2):
            camera.type = "orthographic"
        
        camera.update()


    @controller.event
    def on_resize(width, height):
        controller.program_state["camera"].resize(width, height)

    @controller.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.SPACE:
            print("Jump!")

    @controller.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        if buttons & pyglet.window.mouse.RIGHT:
            controller.program_state["camera"].yaw += dx * 0.01
            controller.program_state["camera"].pitch += dy * 0.01


    # draw loop
    @controller.event
    def on_draw():
        controller.clear()
        graph.draw()
        axis_scene.draw()

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()
