import pyglet
import numpy as np
from pyglet.gl import *


WIDTH = 600
HEIGHT = 600
DEFINITION = 100
TIME = 0

window = pyglet.window.Window(WIDTH, HEIGHT, "Auxiliar 2")


def create_circle(x, y, r, g, b, radius):
    # Discretizamos un circulo en DEFINITION pasos
    # Cada punto tiene 3 coordenadas y 3 componentes de color
    # Consideramos tambien el centro del circulo
    positions = np.zeros((DEFINITION + 1)*3, dtype=np.float32) 
    colors = np.zeros((DEFINITION + 1) * 3, dtype=np.float32)
    dtheta = 2*np.pi / DEFINITION

    for i in range(DEFINITION):
        theta = i*dtheta
        positions[i*3:(i+1)*3] = [x + np.cos(theta)*radius, y + np.sin(theta)*radius, 0.0]
        colors[i*3:(i+1)*3] = [r, g, b]

    # Finalmente agregamos el centro
    positions[3*DEFINITION:] = [x, y, 0.0]
    colors[3*DEFINITION:] = [r, g, b]

    return positions, colors

def create_circle_indices():
    # Ahora calculamos los indices
    indices = np.zeros(3*( DEFINITION + 1 ), dtype=np.int32)
    for i in range(DEFINITION):
        # Cada triangulo se forma por el centro, el punto actual y el siguiente
        indices[3*i: 3*(i+1)] = [DEFINITION, i, i+1]
   
    # Completamos el circulo (pueden borrar esta linea y ver que pasa)
    indices[3*DEFINITION:] = [DEFINITION, DEFINITION - 1, 0]
    return indices

class MyCircle:
    def __init__(self, x, y, r, g, b, radius, pipeline):
        self.position = [x, y]
        self.color = [r, g, b]
        self.radius = radius
        self._buffer = pipeline.vertex_list_indexed(DEFINITION+1, GL_TRIANGLES, create_circle_indices())


    def draw(self):
        cdata, ccolors = create_circle(*self.position, *self.color, self.radius)
        self._buffer.position[:] = cdata
        self._buffer.color[:] = ccolors
        self._buffer.draw(GL_TRIANGLES)



if __name__ == "__main__":
    
    vertex_source = """
#version 330

in vec3 position;
in vec3 color;

out vec3 fragColor;

void main() {
    fragColor = color;
    gl_Position = vec4(position, 1.0f);
}
    """

    fragment_source = """
#version 330

in vec3 fragColor;
out vec4 outColor;

void main()
{
    outColor = vec4(fragColor, 1.0f);
}
    """

    vert_program = pyglet.graphics.shader.Shader(vertex_source, "vertex")
    frag_program = pyglet.graphics.shader.Shader(fragment_source, "fragment")
    pipeline = pyglet.graphics.shader.ShaderProgram(vert_program, frag_program)

    c1 = MyCircle(0.2, 0.2, 1.0, 0.0, 0.0, 0.2, pipeline)
    c2 = MyCircle(-0.2, -0.2, 0.0, 1.0, 0.0, 0.5, pipeline)

    @window.event
    def on_draw():
        glClearColor(0.1, 0.1, 0.1, 0.0)

        #Esta linea limpia la pantalla entre frames
        window.clear()

        with pipeline as _:
            c1.draw()
            c2.draw()

    
    #Añadimos un poco de movimiento
    def update(dt):
        global TIME

        TIME += dt
        #Usando funciones periodicas podemos producir movimiento periodico
        c1.radius = (np.cos(TIME) + 1) * 0.5

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()

    
