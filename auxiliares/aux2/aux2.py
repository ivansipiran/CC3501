import pyglet
from OpenGL.GL import glClearColor
import os
import sys
import time
# No es necesaria la siguiente línea si el archivo está en el root del repositorio
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname((os.path.abspath(__file__))))))
import grafica.transformations as tr

from aux2_pyglet import *
#from aux2_opengl import *

WIDTH = 640
HEIGHT = 640

class Controller(pyglet.window.Window):
    def __init__(self, title, *args, **kargs):
        super().__init__(*args, **kargs)
        self.set_minimum_size(240, 240) # Evita error cuando se redimensiona a 0
        self.set_caption(title)
        self.init()

    def init(self):
        glClearColor(0, 0, 0, 1.0)        

class ModelController():
    def __init__(self):
        self.intensity = 1.0
        # Vector Posición
        self.position = np.array([0, 0, 0], dtype=np.float32)
        # Vector Rotación en ángulos de euler
        self.rotation = np.array([0, 0, 0], dtype=np.float32)
        # Vector Escala        
        self.scale = np.array([1, 1, 1], dtype=np.float32)

    def get_intensity(self):
        return self.intensity

    def get_transform(self):
        translation_matrix = tr.translate(self.position[0], self.position[1], self.position[2])
        # Orden de rotación: primero en Z, luego en Y y finalmente en X
        rotation_matrix = tr.rotationX(self.rotation[0]) @ tr.rotationY(self.rotation[1]) @ tr.rotationZ(self.rotation[2])
        scale_matrix = tr.scale(self.scale[0], self.scale[1], self.scale[2])
        # Orden de transformaciones: primero escala, luego rota y finalmente traslada
        return translation_matrix @ rotation_matrix @ scale_matrix

vertex_source_code = """
    #version 330

    in vec3 position;
    in vec3 color;

    uniform float u_intensity = 1.0f;
    uniform mat4 u_transform = mat4(1.0);

    out vec3 fragColor;

    void main()
    {
        fragColor = color * u_intensity;
        gl_Position = u_transform * vec4(position, 1.0f);
    }
"""

fragment_source_code = """
    #version 330

    in vec3 fragColor;
    out vec4 outColor;

    void main()
    {
        outColor = vec4(fragColor, 1.0f);
    }
""" 

inverted_fragment_source_code = """
    #version 330

    in vec3 fragColor;
    out vec4 outColor;

    void main()
    {
        outColor = vec4(1.0 - fragColor, 1.0f);
    }
""" 

if __name__ == "__main__":
    # Instancia del controller
    controller = Controller("Auxiliar 2", width=WIDTH, height=HEIGHT, resizable=True)

    pipeline = Pipeline(vertex_source_code, fragment_source_code)
    inverted_pipeline  = Pipeline(vertex_source_code, inverted_fragment_source_code)

    #                  x     y    z     r  g  b
    triangle = Model([-0.5, -0.5, 0,    1, 0, 0,
                       0.5, -0.5, 0,    0, 1, 0,
                       0.0,  0.5, 0,    0, 0, 1 ])
    triangle.init_gpu_data(pipeline)
    triangle_controller = ModelController() # Con este objeto se controla la intensidad y la transformación del triángulo

    quad = Model([ -1, -1, 0, 1, 0, 0,
                    1, -1, 0, 0, 1, 0,
                    1,  1, 0, 0, 0, 1,
                   -1,  1, 0, 1, 1, 1 ], [0, 1, 2, 2, 3, 0])
    quad.init_gpu_data(pipeline)
    quad_controller = ModelController() # Con este objeto se controla la intensidad y la transformación del cuadrado

    # en update se actualizan los valores que se le entregan a las uniforms de los shaders
    def update(dt):
        triangle_controller.intensity = np.cos(time.time()) / 2 + 0.5
        quad_controller.intensity = np.sin(time.time() * 2) / 2 + 0.5

    print("Controles:\n\tClick izquierdo y arrastrar: trasladar\n\tClick derecho y arrastrar: rotar\n\tClick central y arrastrar: escalar")
    @controller.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        if buttons & pyglet.window.mouse.LEFT:
            triangle_controller.position[0] += dx / controller.width
            triangle_controller.position[1] += dy / controller.height

        elif buttons & pyglet.window.mouse.RIGHT:
            triangle_controller.rotation[0] += dy / 100
            triangle_controller.rotation[1] -= dx / 100
        
        elif buttons & pyglet.window.mouse.MIDDLE:
            triangle_controller.scale[0] += dx / 1000
            triangle_controller.scale[1] += dy / 1000

    # draw loop
    @controller.event
    def on_draw():
        controller.clear()
        inverted_pipeline.use()
        inverted_pipeline.set_uniform("u_intensity", quad_controller.get_intensity(), "float")
        quad.draw()
        pipeline.use()
        pipeline.set_uniform("u_intensity", triangle_controller.get_intensity(), "float")
        pipeline.set_uniform("u_transform", triangle_controller.get_transform(), "matrix")
        triangle.draw()

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()
