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
from auxiliares.utils.drawables import Model, Texture, DirectionalLight, Material
from auxiliares.utils.colliders import CollisionManager, AABB, Sphere
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
    controller = Controller("Auxiliar 8", width=WIDTH, height=HEIGHT, resizable=True)

    controller.program_state["camera"] = FreeCamera([0, 2.5, 2.5], "perspective")
    controller.program_state["camera"].yaw = -np.pi/ 2
    controller.program_state["camera"].pitch = -np.pi / 3

    color_mesh_pipeline = init_pipeline(
        get_path("auxiliares/shaders/color_mesh.vert"),
        get_path("auxiliares/shaders/color_mesh.frag"))
    
    textured_mesh_pipeline = init_pipeline(
        get_path("auxiliares/shaders/textured_mesh.vert"),
        get_path("auxiliares/shaders/textured_mesh.frag"))
    
    color_mesh_lit_pipeline = init_pipeline(
        get_path("auxiliares/shaders/color_mesh_lit.vert"),
        get_path("auxiliares/shaders/color_mesh_lit.frag"))
    
    textured_mesh_lit_pipeline = init_pipeline(
        get_path("auxiliares/shaders/textured_mesh_lit.vert"),
        get_path("auxiliares/shaders/textured_mesh_lit.frag"))

    cube = Model(shapes.Cube["position"], shapes.Cube["uv"], shapes.Cube["normal"], index_data=shapes.Cube["indices"])
    quad = Model(shapes.Square["position"], shapes.Square["uv"], shapes.Square["normal"], index_data=shapes.Square["indices"])
    sphere = mesh_from_file(get_path("assets/sphere.off"))[0]["mesh"]


    graph = SceneGraph(controller)
    graph.add_node("sun",
                    pipeline=[color_mesh_lit_pipeline, textured_mesh_lit_pipeline],
                    light=DirectionalLight(),
                    rotation=[-np.pi/4, 0, 0],
                   )
    graph.add_node("floor",
                   mesh = quad,
                   pipeline = textured_mesh_lit_pipeline,
                   rotation = [-np.pi/2, 0, 0],
                   texture=Texture("assets/wall1.jpg"),
                   scale = [5, 5, 1],
                   material = Material())
    
    graph.add_node("controllable",
                     mesh = sphere,
                     pipeline = color_mesh_lit_pipeline,
                     position=[0, 0, -2],
                     material = Material())

    graph.add_node("static_cube",
                    mesh = cube,
                    pipeline = color_mesh_lit_pipeline,
                    material = Material(),
                    position = [-2, 0, 0])

    graph.add_node("moving_cube",
                    mesh = cube,
                    pipeline = color_mesh_lit_pipeline,
                    material = Material(),
                    position = [2, 0, 0])
    
    collision_manager = CollisionManager()

    controllable_collider = Sphere("controllable", 0.5)
    #controllable_collider = AABB("controllable", np.array([-0.5, -0.5, -0.5]), np.array([0.5, 0.5, 0.5]))
    controllable_collider.set_position(graph.find_position("controllable"))
    collision_manager.add_collider(controllable_collider)

    static_cube_collider = AABB("static_cube", np.array([-0.5, -0.5, -0.5]), np.array([0.5, 0.5, 0.5]))
    static_cube_collider.set_position(graph.find_position("static_cube"))
    collision_manager.add_collider(static_cube_collider)

    moving_cube_collider = AABB("moving_cube", np.array([-0.5, -0.5, -0.5]), np.array([0.5, 0.5, 0.5]))
    moving_cube_collider.set_position(graph.find_position("moving_cube"))
    collision_manager.add_collider(moving_cube_collider)

    def update(dt):
        controller.program_state["total_time"] += dt
        camera = controller.program_state["camera"]
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

        graph["moving_cube"]["position"][0] = np.cos(controller.program_state["total_time"]) * 2

        # Hay que actualizar las posiciones de cada collider en cada frame
        controllable_collider.set_position(graph.find_position("controllable"))
        # a pesar de que static_cube no se mueve, hay que actualizarlo ya que el grafo de escena es quien actualiza su posición,
        # inicialmente su posición es 0, 0, 0 y cambia en el primer frame dibujado
        static_cube_collider.set_position(graph.find_position("static_cube"))
        moving_cube_collider.set_position(graph.find_position("moving_cube"))

        # Aqui pregunto por el objeto al que quiero hacerle la consulta
        collision_result = collision_manager.check_collision("controllable")

        graph["controllable"]["material"].diffuse = [1, 1, 1]
        graph["static_cube"]["material"].diffuse = [1, 1, 1]
        graph["moving_cube"]["material"].diffuse = [1, 1, 1]

        if len(collision_result) != 0:
            for c in collision_result:
                graph[c]["material"].diffuse = [1, 0, 0]

        

        controllable = graph["controllable"]

        if controller.is_key_pressed(pyglet.window.key.LEFT):
            controllable["position"][0] -= dt

        if controller.is_key_pressed(pyglet.window.key.RIGHT):
            controllable["position"][0] += dt

        if controller.is_key_pressed(pyglet.window.key.UP):
            controllable["position"][2] -= dt

        if controller.is_key_pressed(pyglet.window.key.DOWN):
            controllable["position"][2] += dt

        if controller.is_key_pressed(pyglet.window.key.SPACE):
            controllable["rotation"][1] += dt

        if controller.is_key_pressed(pyglet.window.key.LSHIFT):
            controllable["rotation"][1] -= dt

    @controller.event
    def on_resize(width, height):
        controller.program_state["camera"].resize(width, height)

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

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()
