import pyglet
from OpenGL import GL
import numpy as np
import trimesh as tm
import os
import sys
from pathlib import Path
# No es necesaria la siguiente línea si el archivo está en el root del repositorio
sys.path.append(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))
import grafica.transformations as tr
import utils.shapes as shapes

WIDTH = 640
HEIGHT = 640

class Controller(pyglet.window.Window):
    def __init__(self, title, *args, **kargs):
        super().__init__(*args, **kargs)
        self.set_minimum_size(240, 240) # Evita error cuando se redimensiona a 0
        self.set_caption(title)
        self.key_handler = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.key_handler)
        self.init()

    def init(self):
        GL.glClearColor(1, 1, 1, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        GL.glFrontFace(GL.GL_CCW)

    def is_key_pressed(self, key):
        return self.key_handler[key]

class Model():
    def __init__(self, position_data, color_data, index_data=None):
        self.position_data = position_data
        self.color_data = color_data

        self.index_data = index_data
        if index_data is not None:
            self.index_data = np.array(index_data, dtype=np.uint32)

        self.gpu_data = None

        self.position = np.array([0, 0, 0], dtype=np.float32)
        self.rotation = np.array([0, 0, 0], dtype=np.float32)
        self.scale = np.array([1, 1, 1], dtype=np.float32)

    def init_gpu_data(self, pipeline):
        if self.index_data is not None:
            self.gpu_data = pipeline.vertex_list_indexed(len(self.position_data) // 3, GL.GL_TRIANGLES, self.index_data)
        else:
            self.gpu_data = pipeline.vertex_list(len(self.position_data) // 3, GL.GL_TRIANGLES)
        
        self.gpu_data.position[:] = self.position_data
        self.gpu_data.color[:] = self.color_data

    def draw(self, mode = GL.GL_TRIANGLES):
        self.gpu_data.draw(mode)

    def get_transform(self):
        translation_matrix = tr.translate(self.position[0], self.position[1], self.position[2])
        rotation_matrix = tr.rotationX(self.rotation[0]) @ tr.rotationY(self.rotation[1]) @ tr.rotationZ(self.rotation[2])
        scale_matrix = tr.scale(self.scale[0], self.scale[1], self.scale[2])
        transformation = translation_matrix @ rotation_matrix @ scale_matrix
        return np.reshape(transformation, (16, 1), order="F")

class Mesh(Model):
    def __init__(self, asset_path, base_color = None):
        mesh_data = tm.load(asset_path)
        mesh_scale = tr.uniformScale(2.0 / mesh_data.scale)
        mesh_translate = tr.translate(*-mesh_data.centroid)
        mesh_data.apply_transform( mesh_scale @ mesh_translate)
        vertex_data = tm.rendering.mesh_to_vertexlist(mesh_data)
        indices = vertex_data[3]
        positions = vertex_data[4][1]

        count = len(positions) // 3
        colors = np.full((count * 3, 1), 1.0)
        if base_color is None:
            colors = vertex_data[5][1]
        else:
            for i in range(count):
                colors[i * 3] = base_color[0]
                colors[i * 3 + 1] = base_color[1]
                colors[i * 3 + 2] = base_color[2]

        super().__init__(positions, colors, indices)

class Camera():
    def __init__(self, camera_type = "perspective"):
        self.position = np.array([1, 0, 0], dtype=np.float32)
        self.focus = np.array([0, 0, 0], dtype=np.float32)
        self.type = camera_type

    def update(self):
        pass

    def get_view(self):
        lookAt_matrix = tr.lookAt(self.position, self.focus, np.array([0, 1, 0], dtype=np.float32))
        return np.reshape(lookAt_matrix, (16, 1), order="F")

    def get_projection(self, width, height):
        if self.type == "perspective":
            perspective_matrix = tr.perspective(90, width / height, 0.01, 100)
        elif self.type == "orthographic":
            depth = self.position - self.focus
            depth = np.linalg.norm(depth)
            perspective_matrix = tr.ortho(-(width/height) * depth, (width/height) * depth, -1 * depth, 1 * depth, 0.01, 100)
        return np.reshape(perspective_matrix, (16, 1), order="F")

class OrbitCamera(Camera):
    def __init__(self, distance, camera_type = "perspective"):
        super().__init__(camera_type)
        self.distance = distance
        self.phi = 0
        self.theta = np.pi / 2
        self.update()

    def update(self):
        if self.theta > np.pi:
            self.theta = np.pi
        elif self.theta < 0:
            self.theta = 0.0001

        self.position[0] = self.distance * np.sin(self.theta) * np.sin(self.phi)
        self.position[1] = self.distance * np.cos(self.theta)
        self.position[2] = self.distance * np.sin(self.theta) * np.cos(self.phi)


if __name__ == "__main__":
    # Instancia del controller
    controller = Controller("Auxiliar 3", width=WIDTH, height=HEIGHT, resizable=True)

    with open(Path(os.path.dirname(__file__)) / "shaders/transform.vert") as f:
        vertex_source_code = f.read()

    with open(Path(os.path.dirname(__file__)) / "shaders/color.frag") as f:
        fragment_source_code = f.read()

    vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_shader = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
    pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

    camera = OrbitCamera(3, "perspective")
    camera.phi = np.pi / 4
    camera.theta = np.pi / 4

    controlled_shape = Mesh("assets/Stanford_Bunny.stl", [0.77, 0.15, 0.23])
    controlled_shape.init_gpu_data(pipeline)

    axes = Model(shapes.Axes["position"], shapes.Axes["color"])
    axes.init_gpu_data(pipeline)

    triangle = Model(shapes.Triangle["position"], shapes.Triangle["color"])
    triangle.init_gpu_data(pipeline)
    triangle.position = np.array([-1, 0, -1], dtype=np.float32)

    cube = Model(shapes.Cube["position"], shapes.Cube["color"], shapes.Cube["indices"])
    cube.init_gpu_data(pipeline)
    cube.position = np.array([1, 0, 1], dtype=np.float32)

    quad = Model(shapes.Square["position"], shapes.Square["color"], shapes.Square["indices"])
    quad.init_gpu_data(pipeline)
    quad.position = np.array([1, 0, -1], dtype=np.float32)

    pyramid = Model(shapes.SquarePyramid["position"], shapes.SquarePyramid["color"], shapes.SquarePyramid["indices"])
    pyramid.init_gpu_data(pipeline)
    pyramid.position = np.array([-1, 0, 1], dtype=np.float32)

    print("Controles Cámara:\n\tWASD: Rotar\n\t Q/E: Acercar/Alejar\n\t1/2: Cambiar tipo")
    def update(dt):
        if controller.is_key_pressed(pyglet.window.key.A):
            camera.phi -= dt
        if controller.is_key_pressed(pyglet.window.key.D):
            camera.phi += dt
        if controller.is_key_pressed(pyglet.window.key.W):
            camera.theta -= dt
        if controller.is_key_pressed(pyglet.window.key.S):
            camera.theta += dt
        if controller.is_key_pressed(pyglet.window.key.Q):
            camera.distance += dt
        if controller.is_key_pressed(pyglet.window.key.E):
            camera.distance -= dt
        if controller.is_key_pressed(pyglet.window.key._1):
            camera.type = "perspective"
        if controller.is_key_pressed(pyglet.window.key._2):
            camera.type = "orthographic"

        camera.update()

    print("Controles Objeto:\n\tClick izquierdo y arrastrar: trasladar\n\tClick derecho y arrastrar: rotar\n\tRueda: escalar")
    @controller.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        if buttons & pyglet.window.mouse.LEFT:
            controlled_shape.position[0] += dx / controller.width
            controlled_shape.position[1] += dy / controller.height

        elif buttons & pyglet.window.mouse.RIGHT:
            controlled_shape.rotation[0] -= dy / 100
            controlled_shape.rotation[1] += dx / 100
    
    @controller.event
    def on_mouse_scroll(x, y, scroll_x, scroll_y):
        controlled_shape.scale[0] += scroll_y / 10
        controlled_shape.scale[1] += scroll_y / 10
        controlled_shape.scale[2] += scroll_y / 10

    # draw loop
    @controller.event
    def on_draw():
        controller.clear()
        pipeline.use()

        pipeline["u_view"] = camera.get_view()
        pipeline["u_projection"] = camera.get_projection(controller.width, controller.height)

        pipeline["u_model"] = axes.get_transform()
        axes.draw(GL.GL_LINES)

        pipeline["u_model"] = triangle.get_transform()
        triangle.draw()
        pipeline["u_model"] = cube.get_transform()
        cube.draw()
        pipeline["u_model"] = quad.get_transform()
        quad.draw()
        pipeline["u_model"] = pyramid.get_transform()
        pyramid.draw()
        pipeline["u_model"] = controlled_shape.get_transform()
        controlled_shape.draw()

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()
