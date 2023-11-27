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
            "curve_index": 0,
            "camera": None }
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

class Curve:
    def __init__(self, segments=10):
        self.segments = segments
        self.points = []

    def __getitem__(self, index):
        return self.points[index % self.segments]

    def generateLine(self, p0, p1):
        self.points = np.linspace(p0, p1, self.segments)

    def generateHermiteCurve(self, p0, p1, t0, t1):
        self.points = np.zeros((self.segments, 3))
        P0 = np.array([p0]).T
        P1 = np.array([p1]).T
        T0 = np.array([t0]).T
        T1 = np.array([t1]).T

        G = np.concatenate((P0, P1, T0, T1), axis=1)
        Mh = np.array([[1, 0, -3, 2],
                       [0, 0, 3, -2],
                       [0, 1, -2, 1],
                       [0, 0, -1, 1]])    

        for i in range(self.segments):
            t = i / (self.segments - 1)
            T = np.array([[1, t, t**2, t**3]]).T
            self.points[i] = (G @ Mh @ T).T
            
    def generateBezierCurve(self, p0, p1, p2, p3):
        self.points = np.zeros((self.segments, 3))
        # Generate a matrix concatenating the columns
        P0 = np.array([p0]).T
        P1 = np.array([p1]).T
        P2 = np.array([p2]).T
        P3 = np.array([p3]).T

        G = np.concatenate((P0, P1, P2, P3), axis=1)
        Mb = np.array([[1, -3, 3, -1],
                       [0, 3, -6, 3],
                       [0, 0, 3, -3],
                       [0, 0, 0, 1]])

        for i in range(self.segments):
            t = i / (self.segments - 1)
            T = np.array([[1, t, t**2, t**3]]).T
            self.points[i] = (G @ Mb @ T).T

    def toModel(self):
        return Model(np.array(self.points).flatten())


if __name__ == "__main__":
    # Instancia del controller
    controller = Controller("Auxiliar 10", width=WIDTH, height=HEIGHT, resizable=True)

    controller.program_state["camera"] = FreeCamera([0, 4, 3], "perspective")
    controller.program_state["camera"].yaw = -np.pi/ 2
    controller.program_state["camera"].pitch = -np.pi / 2.5

    color_mesh_pipeline = init_pipeline(
        get_path("auxiliares/shaders/color_mesh.vert"),
        get_path("auxiliares/shaders/color_mesh.frag"))
    
    axis_scene = init_axis(controller)

    """
    Cubo que se usará para seguir el camino de una curva
    """
    cube = Model(shapes.Cube["position"], shapes.Cube["uv"], shapes.Cube["normal"], index_data=shapes.Cube["indices"])

    graph = SceneGraph(controller)
    graph.add_node('line_cube', mesh=cube, pipeline=color_mesh_pipeline, color=[1, 1, 0], scale=[0.2, 0.2, 0.2])
    graph.add_node('hermite_cube', mesh=cube, pipeline=color_mesh_pipeline, color=[1, 0, 1], scale=[0.2, 0.2, 0.2])
    graph.add_node('bezier_cube', mesh=cube, pipeline=color_mesh_pipeline, color=[0, 1, 1], scale=[0.2, 0.2, 0.2])

    """
    Objetos curva, se inicializan con la cantidad de pasos que tendrá cada segmento
    Se genera la curva y se agrega al grafo para ser dibujada
    """

    segments = 50

    line = Curve(segments)
    line.generateLine([-1, -1, -1], [1, 1, 1])
    graph.add_node(
        'line',
        mesh=line.toModel(),
        pipeline=color_mesh_pipeline,
        color=[1, 1, 0],
        mode = GL.GL_LINE_STRIP)
    
    hermite = Curve(segments)
    hermite.generateHermiteCurve([0, 0, 1], [1, 0, 0], [10, 0, 0], [0, 10, 0])
    graph.add_node(
        'hermite',
        mesh=hermite.toModel(),
        pipeline=color_mesh_pipeline,
        color=[1, 0, 1],
        mode = GL.GL_LINE_STRIP)
    
    bezier = Curve(segments)
    bezier.generateBezierCurve([0, 0, 1], [0, 1, 0], [1, 0, 1], [1, 1, 0])
    graph.add_node(
        'bezier',
        mesh=bezier.toModel(),
        pipeline=color_mesh_pipeline,
        color=[0, 1, 1],
        mode = GL.GL_LINE_STRIP)


    """
    Para que los cubos sepan en que punto de la curva deben estar se asigna un índice a estado del controller
    """
    controller.program_state["curve_index"] = 0

    def update(dt):
        camera = controller.program_state["camera"]

        if controller.is_key_pressed(pyglet.window.key.A):
            camera.position -= camera.right * dt
        if controller.is_key_pressed(pyglet.window.key.D):
            camera.position += camera.right * dt
        if controller.is_key_pressed(pyglet.window.key.W):
            camera.position += camera.forward * dt
        if controller.is_key_pressed(pyglet.window.key.S):
            camera.position -= camera.forward * dt
        
        if controller.is_key_pressed(pyglet.window.key.RIGHT):
            controller.program_state["curve_index"] += 1

        if controller.is_key_pressed(pyglet.window.key.LEFT):
            controller.program_state["curve_index"] -= 1
            
        curveIndex = controller.program_state["curve_index"]
        graph["line_cube"]["position"][0] = line[curveIndex][0]
        graph["line_cube"]["position"][1] = line[curveIndex][1]
        graph["line_cube"]["position"][2] = line[curveIndex][2]

        graph["hermite_cube"]["position"][0] = hermite[curveIndex][0]
        graph["hermite_cube"]["position"][1] = hermite[curveIndex][1]
        graph["hermite_cube"]["position"][2] = hermite[curveIndex][2]

        graph["bezier_cube"]["position"][0] = bezier[curveIndex][0]
        graph["bezier_cube"]["position"][1] = bezier[curveIndex][1]
        graph["bezier_cube"]["position"][2] = bezier[curveIndex][2]

        camera.update()


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
        axis_scene.draw()

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()
