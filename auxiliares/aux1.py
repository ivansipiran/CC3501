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

    # draw loop
    @controller.event
    def on_draw():
        GL.glClearColor(0.5, 0.5, 0.5, 1.0)
        controller.clear()

    pyglet.clock.schedule_interval(controller.update, 1/60)
    pyglet.app.run()