import pyglet
from OpenGL import GL
import numpy as np
import os
from pathlib import Path

if __name__ == "__main__":
    # Ventana de pyglet de 700x700
    win = pyglet.window.Window(700, 700)

    # Inicialización de la figura
    # Vértices de la pirámide
    vertices = np.array(
        [-0.8, -0.8, 0.0,
         0.8, -0.8, 0.0,
         0.8, 0.8, 0.0,
         -0.8, 0.8, 0.0,
         0, 0, 0.0], dtype=np.float32)
    
    # Colores de los vértices
    vertex_colors = np.array(
        [1.0, 0.0, 0.0,
         1.0, 0.0, 0.0,
         0.0, 0.0, 1.0,
         0.0, 0.0, 1.0,
         0.0, 1.0, 0.0], dtype=np.float32)
    
    # Índices de los triángulos que forman la figura
    indices = np.array([0, 1, 4, 4, 1, 2, 2, 3, 4, 4, 3, 0], dtype=np.uint32)

    # Shaders
    # Shader de vértices
    with open(Path(os.path.dirname(__file__)) / "examples/hello_world/vertex_program.glsl") as f:
              vertex_source_code= f.read()

    # Shader de pixeles
    with open(Path(os.path.dirname(__file__)) / "examples/hello_world/fragment_program.glsl") as f:
           fragment_source_code = f.read()

    # Pipeline
    vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_shader = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
    pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

    # Inicialización procesamiento gráfico
    gpu_data = pipeline.vertex_list_indexed(5, GL.GL_TRIANGLES, indices)

    gpu_data.position[:] = vertices
    gpu_data.color[:] =vertex_colors


    # GAME LOOP
    @win.event
    def on_draw():
           GL.glClearColor(0.5, 0.5, 0.5, 1.0)

           win.clear()

           pipeline.use()

           gpu_data.draw(GL.GL_TRIANGLES)

    pyglet.app.run()


