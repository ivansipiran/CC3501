# coding=utf-8
"""Simple simulator for an RGB Raster display with a direct color scheme"""


import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys

__author__ = "Daniel Calderon"
__license__ = "MIT"


# A simple class container to store vertices and indices that define a shape
class Shape:
    def __init__(self, vertices, indices, textureFileName=None):
        self.vertices = vertices
        self.indices = indices
        self.textureFileName = textureFileName

# We will use 32 bits data, so we have 4 bytes
# 1 byte = 8 bits
SIZE_IN_BYTES = 4


# A simple class container to reference a shape on GPU memory
class GPUShape:
    def __init__(self):
        self.vao = 0
        self.vbo = 0
        self.ebo = 0
        self.texture = 0
        self.size = 0


class SimpleShaderProgram:

    def __init__(self):

        vertex_shader = """
            #version 330

            in vec3 position;
            in vec3 color;

            out vec3 newColor;
            void main()
            {
                gl_Position = vec4(position, 1.0f);
                newColor = color;
            }
            """

        fragment_shader = """
            #version 330
            in vec3 newColor;

            out vec4 outColor;
            void main()
            {
                outColor = vec4(newColor, 1.0f);
            }
            """

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))


    def drawShape(self, shape, mode=GL_TRIANGLES):
        assert isinstance(shape, GPUShape)

        # Binding the proper buffers
        glBindVertexArray(shape.vao)
        glBindBuffer(GL_ARRAY_BUFFER, shape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, shape.ebo)

        # 3d vertices + rgb color specification => 3*4 + 3*4 = 24 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        color = glGetAttribLocation(self.shaderProgram, "color")
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        # Render the active element buffer with the active shader program
        glDrawElements(mode, shape.size, GL_UNSIGNED_INT, None)



class SimpleTextureShaderProgram:

    def __init__(self):

        vertex_shader = """
            #version 330

            in vec3 position;
            in vec2 texCoords;

            out vec2 outTexCoords;

            void main()
            {
                gl_Position = vec4(position, 1.0f);
                outTexCoords = texCoords;
            }
            """

        fragment_shader = """
            #version 330

            in vec2 outTexCoords;

            out vec4 outColor;

            uniform sampler2D samplerTex;

            void main()
            {
                outColor = texture(samplerTex, outTexCoords);
            }
            """

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))


    def drawShape(self, shape, mode=GL_TRIANGLES):
        assert isinstance(shape, GPUShape)

        # Binding the proper buffers
        glBindVertexArray(shape.vao)
        glBindBuffer(GL_ARRAY_BUFFER, shape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, shape.ebo)
        glBindTexture(GL_TEXTURE_2D, shape.texture)

        # 3d vertices + 2d texture coordinates => 3*4 + 2*4 = 20 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        texCoords = glGetAttribLocation(self.shaderProgram, "texCoords")
        glVertexAttribPointer(texCoords, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(12))
        glEnableVertexAttribArray(texCoords)

        # Render the active element buffer with the active shader program
        glDrawElements(mode, shape.size, GL_UNSIGNED_INT, None)


def toGPUShape(shape):
    assert isinstance(shape, Shape)

    vertexData = np.array(shape.vertices, dtype=np.float32)
    indices = np.array(shape.indices, dtype=np.uint32)

    # Here the new shape will be stored
    gpuShape = GPUShape()

    gpuShape.size = len(shape.indices)
    gpuShape.vao = glGenVertexArrays(1)
    gpuShape.vbo = glGenBuffers(1)
    gpuShape.ebo = glGenBuffers(1)

    # Vertex data must be attached to a Vertex Buffer Object (VBO)
    glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
    glBufferData(GL_ARRAY_BUFFER, len(vertexData) * SIZE_IN_BYTES, vertexData, GL_STATIC_DRAW)

    # Connections among vertices are stored in the Elements Buffer Object (EBO)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indices) * SIZE_IN_BYTES, indices, GL_STATIC_DRAW)

    return gpuShape


# A class to store the application control
class Controller:
    
    
    def __init__(self):
        self.fillPolygon = True
        self.showGrid = True


def createGPUTextureQuad():
    vertices = [
    #   positions   texture
        -1, -1, 0,  1, 0,
         1, -1, 0,  1, 1,
         1,  1, 0,  0, 1,
        -1,  1, 0,  0, 0]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
         0, 1, 2,
         2, 3, 0]

    return Shape(vertices, indices)


def createGrid(Nx, Ny):

    vertices = []
    indices = []
    index = 0

    # cols
    for x in np.linspace(-1, 1, Nx + 1, True):
        vertices += [x, -1, 0] + [0,0,0]
        vertices += [x,  1, 0] + [0,0,0]
        indices += [index, index+1]
        index += 2

    # rows
    for y in np.linspace(-1, 1, Ny + 1, True):
        vertices += [-1, y, 0] + [0,0,0]
        vertices += [ 1, y, 0] + [0,0,0]
        indices += [index, index+1]
        index += 2

    return Shape(vertices, indices)


class DirectRGBRasterDisplay:


    def __init__(self, windowSize, imageSize, displayName):
        self.windowSize = windowSize
        self.imageSize = imageSize
        self.displayName = displayName
        self.controller = Controller()


    def setMatrix(self, matrix):
        assert(self.imageSize[0] == matrix.shape[0])
        assert(self.imageSize[1] == matrix.shape[1])
        
        # RGB 8 bits for each channel 
        assert(matrix.shape[2] == 3)
        assert(matrix.dtype == np.uint8)

        self.imgData = matrix.reshape((matrix.shape[0] * matrix.shape[1], 3))


    def on_key(self, window, key, scancode, action, mods):

        if action != glfw.PRESS:
            return

        if key == glfw.KEY_SPACE:
            self.controller.showGrid = not self.controller.showGrid

        elif key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(self.window, True)


    def draw(self):
        # Initialize glfw
        if not glfw.init():
            glfw.set_window_should_close(window, True)
    
        self.window = glfw.create_window(self.windowSize[0], self.windowSize[1], self.displayName, None, None)
        glfw.make_context_current(self.window)
        glfw.set_key_callback(self.window, self.on_key)
        
        self.pipeline = SimpleTextureShaderProgram()
        
        self.colorPipeline = SimpleShaderProgram()

        gpuShape = toGPUShape(createGPUTextureQuad())
        gpuGrid = toGPUShape(createGrid(self.imageSize[0], self.imageSize[1]))
        
        gpuShape.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture)

        # texture wrapping params
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        # texture filtering params
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        internalFormat = GL_RGB
        format = GL_RGB

        glTexImage2D(GL_TEXTURE_2D, 0, internalFormat, self.imageSize[1], self.imageSize[0], 0, format, GL_UNSIGNED_BYTE, self.imgData)

        while not glfw.window_should_close(self.window):
            glfw.poll_events()

            if self.controller.fillPolygon:
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

            glClear(GL_COLOR_BUFFER_BIT)
        
            glUseProgram(self.pipeline.shaderProgram)
            self.pipeline.drawShape(gpuShape)
        
            if self.controller.showGrid:
                glUseProgram(self.colorPipeline.shaderProgram)
                self.colorPipeline.drawShape(gpuGrid, GL_LINES)

            # Once the render is done, buffers are swapped, showing only the complete scene.
            glfw.swap_buffers(self.window)
    
        glfw.terminate()


