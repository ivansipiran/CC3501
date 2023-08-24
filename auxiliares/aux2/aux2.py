import pyglet
from OpenGL.GL import glClearColor
from pathlib import Path
import os
import time
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

vertex_source_code = """
    #version 330

    in vec3 position;
    in vec3 color;

    out vec3 fragColor;

    void main()
    {
        fragColor = color;
        gl_Position = vec4(position, 1.0f);
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

if __name__ == "__main__":
    # Instancia del controller
    controller = Controller("Auxiliar 2", width=WIDTH, height=HEIGHT, resizable=True)

    pipeline = Pipeline(vertex_source_code, fragment_source_code)

    #                  x     y    z     r  g  b
    triangle = Model([-0.5, -0.5, 0,    1, 0, 0,
                       0.5, -0.5, 0,    0, 1, 0,
                       0.0,  0.5, 0,    0, 0, 1 ])
    triangle.init_gpu_data(pipeline)

    def update(dt):
        pass

    @controller.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        if buttons & pyglet.window.mouse.LEFT:
            pass

        elif buttons & pyglet.window.mouse.RIGHT:
            pass
        
        elif buttons & pyglet.window.mouse.MIDDLE:
            pass

    # draw loop
    @controller.event
    def on_draw():
        controller.clear()
        pipeline.use()
        triangle.draw()

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()
