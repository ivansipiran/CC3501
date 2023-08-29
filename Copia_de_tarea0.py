import pyglet
from OpenGL import GL
import numpy as np
#import os
from pathlib import Path

if __name__ == "__main__":
    # Creación de la ventana
    win = pyglet.window.Window(700, 700)
    win.set_caption("Tarea 0: vista 'frontal' de un dado de 8 caras")

    # Shaders
    # Código del vertex shader
    vertex_source_code = """
        #version 330

        in vec2 position;
        in vec3 color;
        in float intensity;

        out vec3 fragColor;
        out float fragIntensity;

        void main()
        {
            fragColor = color;
            fragIntensity = intensity;
            gl_Position = vec4(position, 0.0f, 1.0f);
        }
    """

    # Código del fragment shader
    fragment_source_code = """
        #version 330

        in vec3 fragColor;
        in float fragIntensity;
        out vec4 outColor;

        void main()
        {
            outColor = fragIntensity * vec4(fragColor, 1.0f);
        }
    """

    # Inicialización de la figura
    # Vértices del octaedro (o 'dado' de 8 caras)

    # Cara frontal: rojo -> azul
    vertices_front = np.array(
        [-0.75, -0.25,
         0.75, -0.25,
         0.0, 0.85], dtype=np.float32)
    vertex_colors_front = np.array(
        [0.0, 0.3, 1.0,
         0.0, 0.3, 1.0,
         0.0, 0.3, 1.0], dtype=np.float32)
    index_front = np.array([0, 1, 2], dtype=np.uint32)

    # Cara izquierda: verde
    vertices_left = np.array(
        [-0.75, -0.25,
         0.0, 0.85,
         -0.75, 0.28], dtype=np.float32)
    vertex_colors_left = np.array(
        [0.0, 0.8, 0.6,
         0.0, 0.8, 0.6,
         0.0, 0.8, 0.6], dtype=np.float32)
    index_left = np.array([0, 1, 2], dtype=np.uint32)

    # Cara derecha: gris claro
    vertices_right = np.array(
        [0.75, -0.25,
         0.75, 0.28,
         0.0, 0.85], dtype=np.float32)
    vertex_colors_right = np.array(
        [0.85, 0.85, 1.0,
         0.85, 0.85, 1.0,
         0.85, 0.85, 1.0], dtype=np.float32)
    index_right = np.array([0, 1, 2], dtype=np.uint32)

    # Cara basal: azul -> rojo
    vertices_base = np.array(
        [-0.75, -0.25,
         0.0, -0.8,
         0.75, -0.25], dtype=np.float32)
    vertex_colors_base = np.array(
        [1.0, 0.2, 0.0,
         1.0, 0.2, 0.0,
         1.0, 0.2, 0.0], dtype=np.float32)
    index_base = np.array([0, 1, 2], dtype=np.uint32)

    indexes = np.array([0, 1, 2], dtype=np.uint32)
    intensities = np.array(
        [1.0, 1.0, 1.0], dtype=np.float32)

    # Cargar shaders
    vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_shader = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
    pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

    # Datos GPU
    # Cara frontal
    gpu_data_front = pipeline.vertex_list_indexed(3, GL.GL_TRIANGLES, indexes)
    gpu_data_front.position[:] = vertices_front
    gpu_data_front.color[:] = vertex_colors_front
    gpu_data_front.intensity = intensities

    # Cara izquierda
    gpu_data_left = pipeline.vertex_list_indexed(3, GL.GL_TRIANGLES, indexes)
    gpu_data_left.position[:] = vertices_left
    gpu_data_left.color[:] = vertex_colors_left
    gpu_data_left.intensity = intensities

    # Cara derecha
    gpu_data_right = pipeline.vertex_list_indexed(3, GL.GL_TRIANGLES, indexes)
    gpu_data_right.position[:] = vertices_right
    gpu_data_right.color[:] = vertex_colors_right
    gpu_data_right.intensity = intensities
    
    # Cara basal
    gpu_data_base = pipeline.vertex_list_indexed(3, GL.GL_TRIANGLES, indexes)
    gpu_data_base.position[:] = vertices_base
    gpu_data_base.color[:] = vertex_colors_base
    gpu_data_base.intensity = intensities



    # GAME LOOP
    @win.event
    def on_draw():
        GL.glClearColor(0.5, 0.5, 0.5, 1.0)
        win.clear()
        pipeline.use()
        gpu_data_front.draw(GL.GL_TRIANGLES)
        gpu_data_left.draw(GL.GL_TRIANGLES)
        gpu_data_right.draw(GL.GL_TRIANGLES)
        gpu_data_base.draw(GL.GL_TRIANGLES)
    

    pyglet.app.run()


