import pyglet
from OpenGL import GL
import numpy as np
from pathlib import Path
import os

WIDTH = 640
HEIGHT = 640

class Controller(pyglet.window.Window):
    def __init__(self, title, *args, **kargs):
        super().__init__(*args, **kargs)
        self.set_minimum_size(240, 240) # Evita error cuando se redimensiona a 0
        self.set_caption(title)

    def update(self, dt):
        pass

if __name__ == "__main__":
    # Instancia del controller
    controller = Controller("Auxiliar 1", width=WIDTH, height=HEIGHT, resizable=True)
    
    # Cargar archivos y asignarlos a variables
    with open(Path(os.path.dirname(__file__)) / "shaders/basic.vert") as f:
        vertex_source_code = f.read()

    with open(Path(os.path.dirname(__file__)) / "shaders/basic.frag") as f:
        fragment_source_code = f.read()

    vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_shader = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
    pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

    positions = np.array([
        -0.5, -0.5,
         0.5, -0.5, 
         0.0,  0.5
    ], dtype=np.float32)

    colors = np.array([
        1, 0, 0,
        0, 1, 0,
        0, 0, 1
    ], dtype=np.float32)

    intensities = np.array([
        1, 0.5, 0
    ], dtype=np.float32)

    gpu_triangle = pipeline.vertex_list(3, GL.GL_TRIANGLES)
    gpu_triangle.position = positions
    gpu_triangle.color = colors
    gpu_triangle.intensity = intensities

    quad_positions = np.array([
        -1, -1,
        1, -1,
        1,  1,
        -1,  1
    ], dtype=np.float32)

    quad_colors = np.array([
        1, 0, 0,
        0.0, 1.0, 0.0, # verde
        0.0, 0.0, 1.0, # azul
        1.0, 1.0, 1.0  # blanco
    ], dtype=np.float32)

    quad_intensities = np.array([1, 1, 1, 1], dtype=np.float32)

    quad_indices = np.array([
        0, 1, 2,
        2, 3, 0
    ], dtype=np.uint32)

    gpu_quad = pipeline.vertex_list_indexed(4, GL.GL_TRIANGLES, quad_indices)
    gpu_quad.position = quad_positions
    gpu_quad.color = quad_colors
    gpu_quad.intensity = quad_intensities

    # draw loop
    @controller.event
    def on_draw():
        GL.glClearColor(0, 0, 0, 1.0)
        controller.clear()
        pipeline.use()
        gpu_quad.draw(GL.GL_TRIANGLES)
        gpu_triangle.draw(GL.GL_TRIANGLES)

    pyglet.clock.schedule_interval(controller.update, 1/60)
    pyglet.app.run()