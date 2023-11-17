import pyglet
from OpenGL import GL
import numpy as np
import sys
from Box2D import b2EdgeShape, b2CircleShape, b2World

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
from auxiliares.utils.drawables import Model, DirectionalLight, Material, PointLight
from auxiliares.utils.helpers import init_axis, init_pipeline, mesh_from_file, get_path
import grafica.transformations as tr

WIDTH = 640
HEIGHT = 640

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

    controller.program_state["camera"] = FreeCamera([0, 2.5, 2.5], "perspective")
    controller.program_state["camera"].yaw = -np.pi/ 2
    controller.program_state["camera"].pitch = -np.pi / 4

    color_mesh_pipeline = init_pipeline(
        get_path("auxiliares/shaders/color_mesh.vert"),
        get_path("auxiliares/shaders/color_mesh.frag"))
    
    axis_scene = init_axis(controller)

    quad = Model(shapes.Square["position"], shapes.Square["uv"], shapes.Square["normal"], index_data=shapes.Square["indices"])
    sphere = mesh_from_file("assets/sphere.off")[0]["mesh"]

    graph = SceneGraph(controller)

    graph.add_node("ball",
                   mesh =sphere,
                   pipeline = color_mesh_pipeline,
                   scale=[0.5, 0.5, 0.5],
                   color=[1, 0, 0]
                   )
    graph.add_node("ground1",
                    mesh=quad,
                    pipeline=color_mesh_pipeline,
                    position=[-5, -0.5, 0],
                    scale=[5, 1, 1],
                    color=[0, 0, 1]
                    )
    
    graph.add_node("ground2",
                    mesh=quad,
                    pipeline=color_mesh_pipeline,
                    scale=[2.5, 1, 1],
                    position=[-2, 0.5, 0.01],
                    rotation=[0, 0, np.pi/4],
                    color=[0, 1, 0]
                    )
                    
    graph.add_node("ground3",
                    mesh=quad,
                    pipeline=color_mesh_pipeline,
                    scale=[2, 1, 1],
                    position=[-0.5, 1.22, 0],
                    color=[0, 0, 1]
                    )
    
    graph.add_node("ground4",
                    mesh=quad,
                    pipeline=color_mesh_pipeline,
                    scale=[2, 1, 1],
                    position=[2, 1.22, 0],
                    color=[0, 0, 1]
                    )
    
    graph.add_node("ground5",
                    mesh=quad,
                    pipeline=color_mesh_pipeline,
                    scale=[2.5, 1, 1],
                    position=[3.5, 0.5, 0.01],
                    rotation=[0, 0, -np.pi/4],
                    color=[0, 1, 0]
                    )
    
    graph.add_node("ground6",
                    mesh=quad,
                    pipeline=color_mesh_pipeline,
                    position=[6, -0.5, 0],
                    scale=[4, 1, 1],
                    color=[0, 0, 1]
                    )

    def update_world(dt):
        controller.program_state["total_time"] += dt

    def update(dt):
        update_world(dt)
        camera = controller.program_state["camera"]

        controllable = graph["ball"]

        if controller.is_key_pressed(pyglet.window.key.D):
            controllable["position"][0] += 2*dt
        if controller.is_key_pressed(pyglet.window.key.A):
            controllable["position"][0] -= 2*dt
        if controller.is_key_pressed(pyglet.window.key._1):
            camera.type = "perspective"
        if controller.is_key_pressed(pyglet.window.key._2):
            camera.type = "orthographic"
        
        camera.position[0] = controllable["position"][0]
        camera.position[1] = controllable["position"][1] + 2.5

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
