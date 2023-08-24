import pyglet
from OpenGL import GL
import numpy as np
from pathlib import Path
import os
import sys
# No es necesaria la siguiente línea si el archivo está en el root del repositorio
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname((os.path.abspath(__file__))))))
import grafica.transformations as tr

print("Implementación de Pyglet")

class Pipeline(pyglet.graphics.shader.ShaderProgram):
    def __init__(self, vertex_source, fragment_source):
        vert_shader = pyglet.graphics.shader.Shader(vertex_source, "vertex")
        frag_shader = pyglet.graphics.shader.Shader(fragment_source, "fragment")
        super().__init__(vert_shader, frag_shader)

    def set_uniform(self, name, value, type):
        uniform = self[name]
        if uniform is None:
            print(f"Warning: Uniform {name} does not exist")
            return

        if type == "matrix":
            self[name] = np.reshape(value, (16, 1), order="F")
        elif type == "float":
            self[name] = value

class Model():
    def __init__(self, vertex_data, index_data=None):
        count = len(vertex_data) // 6
        vertex_data = np.array(vertex_data, dtype=np.float32)
        vertex_data.shape = (count, 6)
        self.position_data = vertex_data[:, 0:3].flatten()
        self.color_data = vertex_data[:, 3:6].flatten()

        self.index_data = index_data
        if index_data is not None:
            self.index_data = np.array(index_data, dtype=np.uint32)

        self.gpu_data = None

    def init_gpu_data(self, pipeline):
        if self.index_data is not None:
            self.gpu_data = pipeline.vertex_list_indexed(len(self.position_data) // 3, GL.GL_TRIANGLES, self.index_data)
        else:
            self.gpu_data = pipeline.vertex_list(len(self.position_data) // 3, GL.GL_TRIANGLES)
        
        self.gpu_data.position[:] = self.position_data
        self.gpu_data.color[:] = self.color_data

    def draw(self, mode = GL.GL_TRIANGLES):
        self.gpu_data.draw(mode)
