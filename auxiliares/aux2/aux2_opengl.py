import pyglet
from OpenGL.GL import *
import numpy as np
from pathlib import Path
import os
import sys
# No es necesaria la siguiente línea si el archivo está en el root del repositorio
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname((os.path.abspath(__file__))))))
import grafica.transformations as tr

SIZE_IN_BYTES = 4

print("Implementación de OpenGL")

class Pipeline():
    def __init__(self, vertex_source, fragment_source):
        vert_shader = glCreateShader(GL_VERTEX_SHADER)  # Creo un vertex shader
        glShaderSource(vert_shader, vertex_source)  # Le asigno el código fuente
        glCompileShader(vert_shader)    # Compilo el shader

        frag_shader = glCreateShader(GL_FRAGMENT_SHADER)    # Creo un fragment shader
        glShaderSource(frag_shader, fragment_source)    # Le asigno el código fuente
        glCompileShader(frag_shader)    # Compilo el shader

        self.program = glCreateProgram()    # Creo un programa de shaders
        glAttachShader(self.program, vert_shader)   # Adjunto el vertex shader
        glAttachShader(self.program, frag_shader)   # Adjunto el fragment shader
        glLinkProgram(self.program) # Linkeo el programa

    def use(self):
        glUseProgram(self.program)  # Activo el programa

    def setupVertexAttributes(self):
        # 3 floats + 3 floats
        stride = 3 * SIZE_IN_BYTES + 3 * SIZE_IN_BYTES

        # Posiciones
        position = glGetAttribLocation(self.program, "position")
        position_size = 3
        glVertexAttribPointer(position, position_size, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        # Colores
        color = glGetAttribLocation(self.program, "color")
        color_size = 3
        glVertexAttribPointer(color, color_size, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)
    
    def set_uniform(self, name, value, type):
        location = glGetUniformLocation(self.program, name)

        if location == -1:
            print(f"Warning: Uniform {name} does not exist")
            return

        if type == "matrix":
            glUniformMatrix4fv(location, 1, GL_TRUE, value)
        elif type == "float":
            glUniform1f(location, value)
    

class Model():
    def __init__(self, vertex_data, index_data=None):
        self.vertex_data = np.array(vertex_data, dtype=np.float32)

        self.index_data = index_data
        if index_data is not None:
            self.index_data = np.array(index_data, dtype=np.uint32)

    def init_gpu_data(self, pipeline):
        self.vao = glGenVertexArrays(1) # Genero un VAO
        glBindVertexArray(self.vao) # Lo selecciono
        
        self.vbo = glGenBuffers(1)  # Genero un VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo) # Lo selecciono
        glBufferData(GL_ARRAY_BUFFER, len(self.vertex_data) * SIZE_IN_BYTES, self.vertex_data, GL_STATIC_DRAW) # Cargo los datos

        if self.index_data is not None:
            self.ebo = glGenBuffers(1)  # Genero un EBO si es que hay índices
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo) # Lo selecciono
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(self.index_data) * SIZE_IN_BYTES, self.index_data, GL_STATIC_DRAW)    # Cargo los datos

        pipeline.setupVertexAttributes()    # Configuro el VAO con los atributos del pipeline

        glBindVertexArray(0)    # Deselecciono el VAO

    def draw(self, mode = GL_TRIANGLES):
        glBindVertexArray(self.vao) # Selecciono el VAO
        if self.index_data is not None:
            glDrawElements(mode, len(self.vertex_data), GL_UNSIGNED_INT, None)  # Dibujo con índices
        else:
            glDrawArrays(mode, 0, len(self.vertex_data))    # Dibujo sin índices
        
        glBindVertexArray(0)    # Deselecciono el VAO
