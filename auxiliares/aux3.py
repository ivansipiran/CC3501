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
        #GL.glEnable(GL.GL_DEPTH_TEST)
        #GL.glEnable(GL.GL_CULL_FACE)
        #GL.glCullFace(GL.GL_BACK)
        #GL.glFrontFace(GL.GL_CCW)

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

    controlled_shape = Model(shapes.Triangle["position"], shapes.Triangle["color"])
    controlled_shape.init_gpu_data(pipeline)

    axes = Model(shapes.Axes["position"], shapes.Axes["color"])
    axes.init_gpu_data(pipeline)

    def update(dt):
        pass

    print("Controles:\n\tClick izquierdo y arrastrar: trasladar\n\tClick derecho y arrastrar: rotar\n\tRueda: escalar")
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

        pipeline["u_model"] = axes.get_transform()
        axes.draw(GL.GL_LINES)

        pipeline["u_model"] = controlled_shape.get_transform()
        controlled_shape.draw()

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()
