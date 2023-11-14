import pyglet
from OpenGL import GL
import numpy as np
import sys
from Box2D import b2PolygonShape, b2World
import grafica.transformations as tr

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
    controller = Controller("Demo", width=WIDTH, height=HEIGHT, resizable=True)

    controller.program_state["camera"] = FreeCamera([0, 0, 0], "perspective")
    controller.program_state["camera"].pitch = -np.pi / 8
    
    axis_scene = init_axis(controller)

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
    pyramid = Model(shapes.SquarePyramid["position"], shapes.SquarePyramid["uv"], shapes.SquarePyramid["normal"], index_data=shapes.SquarePyramid["indices"])
    quad = Model(shapes.Square["position"], shapes.Square["uv"], shapes.Square["normal"], index_data=shapes.Square["indices"])
    sphere = mesh_from_file("assets/sphere.off")[0]["mesh"]

    bricks = Texture("assets/bricks.jpg")
    wall2 = Texture("assets/wall2.jpg")

    graph = SceneGraph(controller)

    graph.add_node("sun",
                   pipeline=[color_mesh_lit_pipeline, textured_mesh_lit_pipeline],
                   position=[0, 2, 0],
                   rotation=[-np.pi/4, 0, 0],
                   light=DirectionalLight(diffuse = [1, 1, 1], specular = [0.25, 0.25, 0.25], ambient = [0.15, 0.15, 0.15]))

    zorzal = mesh_from_file("assets/zorzal.obj")
    graph.add_node("zorzal")
    for i in range(len(zorzal)):
        graph.add_node(zorzal[i]["id"],
                    attach_to="zorzal",
                    mesh=zorzal[i]["mesh"],
                    pipeline=textured_mesh_lit_pipeline,
                    material=Material(),
                    texture=zorzal[i]["texture"],
                    cull_face=False)
    graph.add_node("point_light",
                    attach_to="zorzal",
                    pipeline=[color_mesh_lit_pipeline, textured_mesh_lit_pipeline],
                    light=PointLight(diffuse = [0, 1, 1], specular = [1, 1, 0], ambient = [0.1, 0.1, 0.1]))
    
    graph.add_node("spotlight",
                    pipeline=[color_mesh_lit_pipeline, textured_mesh_lit_pipeline],
                    light=SpotLight(diffuse = [1, 1, 1], specular = [1, 1, 1], ambient = [0.1, 0.1, 0.1]),
                    position=[0, 2, 8],
                    rotation=[-np.pi/2, 0, 0])
    
        
    graph.add_node("cube",
                   mesh = cube,
                   pipeline = textured_mesh_lit_pipeline,
                   texture = bricks,
                   material = Material(
                          diffuse = [1, 0, 0],
                          specular = [1, 0, 1],
                          ambient = [0.1, 0, 0],
                          shininess = 128
                     ))
    
    graph.add_node("danger_sphere",
                     mesh = sphere,
                     pipeline = color_mesh_pipeline,
                     color = [1, 0, 0]
                    )

    graph.add_node("pyramid",
                     mesh = pyramid,
                     pipeline = textured_mesh_lit_pipeline,
                     material = Material(
                          diffuse = [0, 0, 1],
                          specular = [0, 1, 0],
                          ambient = [0.1, 0, 0],
                          shininess = 32
                     ))

    graph.add_node("floor",
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
    
    ########## Simulación Física ##########
    world = b2World(gravity=(0, 0))

    # Objetos estáticos
    wall1_body = world.CreateStaticBody(position=(-10, 0))
    wall1_body.CreatePolygonFixture(box=(0.5, 10), density=1, friction=1)

    wall2_body = world.CreateStaticBody(position=(10, 0))
    wall2_body.CreatePolygonFixture(box=(0.5, 10), density=1, friction=1)

    wall3_body = world.CreateStaticBody(position=(0, -10))
    wall3_body.CreatePolygonFixture(box=(10, 0.5), density=1, friction=1)

    wall4_body = world.CreateStaticBody(position=(0, 10))
    wall4_body.CreatePolygonFixture(box=(10, 0.5), density=1, friction=1)

    winzone_body = world.CreateStaticBody(position=(0, 8))
    winzoneFixture = winzone_body.CreateCircleFixture(radius=1, density=1, friction=1)
    winzoneFixture.sensor = True # No interactúa con otros objetos en la simulación física, solo detecta colisiones

    # Objetos dinámicos
    zorzal_body = world.CreateDynamicBody(position=(0, -5))
    zorzal_body.CreatePolygonFixture(box=(0.5, 0.5), density=1, friction=1)

    box_body = world.CreateDynamicBody(position=(-2, -2))
    box_body.CreatePolygonFixture(box=(0.5, 0.5), density=1, friction=1)

    pyramid_body = world.CreateDynamicBody(position=(2, -2))
    pyramid_body.CreatePolygonFixture(box=(0.5, 0.5), density=1, friction=1)

    danger_body = world.CreateDynamicBody(position=(0, 5))
    danger_body.CreateCircleFixture(radius=0.5, density=100, friction=1)

    # Se guardan los cuerpos en el controller para poder acceder a ellos desde el loop de simulación
    controller.program_state["world"] = world
    controller.program_state["bodies"]["zorzal"] = zorzal_body
    controller.program_state["bodies"]["box"] = box_body
    controller.program_state["bodies"]["pyramid"] = pyramid_body
    controller.program_state["bodies"]["danger"] = danger_body
    controller.program_state["bodies"]["winzone"] = winzone_body

    #######################################

    # Aquí se actualizan los parámetros de la simulación física
    def update_world(dt):
        world = controller.program_state["world"]
        world.Step(
            dt, controller.program_state["vel_iters"], controller.program_state["pos_iters"]
        )
        world.ClearForces()

    def update(dt):
        controller.program_state["total_time"] += dt
        camera = controller.program_state["camera"]

        # Actualización física del zorzal
        zorzal_body = controller.program_state["bodies"]["zorzal"]
        graph["zorzal"]["transform"] = tr.translate(zorzal_body.position[0], 0, zorzal_body.position[1]) @ tr.rotationY(-zorzal_body.angle)

        # Actualización física de la caja
        box_body = controller.program_state["bodies"]["box"]
        graph["cube"]["transform"] = tr.translate(box_body.position[0], 0, box_body.position[1]) @ tr.rotationY(-box_body.angle)

        # Actualización física de la pirámide
        pyramid_body = controller.program_state["bodies"]["pyramid"]
        graph["pyramid"]["transform"] = tr.translate(pyramid_body.position[0], 0, pyramid_body.position[1]) @ tr.rotationY(-pyramid_body.angle)

        # Actualización física de la caja peligrosa
        danger_body = controller.program_state["bodies"]["danger"]
        danger_body.position = (5 * np.cos(controller.program_state["total_time"] * 2), 5)
        danger_body.linearVelocity = (10, 10)
        graph["danger_sphere"]["transform"] = tr.translate(danger_body.position[0], 0, danger_body.position[1]) @ tr.rotationY(-danger_body.angle)

        # Check condición de victoria, zorzal en winzone
        winzone_body = controller.program_state["bodies"]["winzone"]
        if winzone_body.fixtures[0].TestPoint(zorzal_body.position):
            print("Ganaste!")
            pyglet.app.exit()
        

        # Modificar la fuerza y el torque del zorzal con las teclas
        zorzal_forward = np.array([np.sin(-zorzal_body.angle), 0, np.cos(-zorzal_body.angle)])
        if controller.is_key_pressed(pyglet.window.key.A):
            zorzal_body.ApplyTorque(-0.5, True)
        if controller.is_key_pressed(pyglet.window.key.D):
            zorzal_body.ApplyTorque(0.5, True)
        if controller.is_key_pressed(pyglet.window.key.W):
            zorzal_body.ApplyForce((zorzal_forward[0], zorzal_forward[2]), zorzal_body.worldCenter, True)
        if controller.is_key_pressed(pyglet.window.key.S):
            zorzal_body.ApplyForce((-zorzal_forward[0], -zorzal_forward[2]), zorzal_body.worldCenter, True)

        camera.position[0] = zorzal_body.position[0] + 2 * np.sin(zorzal_body.angle)
        camera.position[1] = 2
        camera.position[2] = zorzal_body.position[1] - 2 * np.cos(zorzal_body.angle)
        camera.yaw = zorzal_body.angle + np.pi / 2
        camera.update()
        update_world(dt)

    @controller.event
    def on_key_press(symbol, modifiers):
        zorzal_body = controller.program_state["bodies"]["zorzal"]
        # Reset zorzal
        if symbol == pyglet.window.key.SPACE:
            zorzal_body.position = (0, -5)
            zorzal_body.angle = 0
            zorzal_body.linearVelocity = (0, 0)
            zorzal_body.angularVelocity = 0
            

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
        axis_scene.draw()
        graph.draw()

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()
