import pyglet
import numpy as np
from pyglet.gl import *


WIDTH = 600
HEIGHT = 600
DEFINITION = 36
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

# Usaremos una clase para llevar los datos de los circulos
class MyCircle:
    def __init__(self, x, y, r, g, b, radius, pipeline):
        self.position = [x, y]
        self.color = [r, g, b]
        self.radius = radius

        # Cada circulo usa siempre el mismo espacio en la memoria 
        self._buffer = pipeline.vertex_list_indexed(DEFINITION+1, GL_TRIANGLES, create_circle_indices())


    def draw(self):
        # Cada vez que dibujemos el circulo tenemos que generar la 
        # geometria
        cdata, ccolors = create_circle(*self.position, *self.color, self.radius)
        self._buffer.position[:] = cdata
        self._buffer.color[:] = ccolors
        self._buffer.draw(GL_TRIANGLES)

if __name__ == "__main__":
    # Creamos nuestros shaders
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

    # Compilamos los shaders
    vert_program = pyglet.graphics.shader.Shader(vertex_source, "vertex")
    frag_program = pyglet.graphics.shader.Shader(fragment_source, "fragment")

    # Creamos nuestro pipeline de rendering
    pipeline = pyglet.graphics.shader.ShaderProgram(vert_program, frag_program)

    # Creamos el circulo
    ca = MyCircle(0.0, 0.0, 0.4, 0.2, 0.0, 0.0, pipeline)
    cb = MyCircle(0.0, 0.0, 0.0, 0.9, 0.3, 0.5, pipeline)
    cc1 = MyCircle(0.0, 0.0, 0.0, 0.4, 0.9, 0.3, pipeline)
    cc2 = MyCircle(0.0, 0.0, 0.5, 0.4, 0.5, 0.1, pipeline)


    @window.event
    def on_draw():
        # Esta linea limpia la pantalla entre frames
        window.clear()
        glClearColor(0.1, 0.1, 0.1, 0.0)

        with pipeline as _:
            # parte a
            # ca.draw()

            # parte b
            # cb.draw()

            # parte c
            cc1.draw()
            cc2.draw()
            


    @window.event
    def update(dt):
        # Aqui actualizamos las variables
        # cada dt segundos
        global TIME

        ca.radius = 0.3*np.sin(TIME) + 0.5
        cb.position[0] = np.cos(TIME)
        cc1.position = [np.cos(TIME), 0.0]
        RADIUS = 0.5
        cc2.position = [cc1.position[0] + RADIUS*np.cos(3*TIME),
                        cc1.position[1] + RADIUS*np.sin(3*TIME)]

        TIME += dt

    
    # Le decimos a pyglet que llame a update cada 1/60 segs
    # Lo que se traduce en 60 actualizaciones por segundo
    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()


    
