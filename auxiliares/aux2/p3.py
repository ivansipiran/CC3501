import pyglet
import numpy as np
from pyglet.gl import *


WIDTH = 600
HEIGHT = 600
DEFINITION = 100

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
    circle_pos, circle_col = create_circle(-0.2, 0.0, 0.7, 0.5, 0.0, 0.5)

    # Creamos el circulo en la gpu, ahora con menos vertices en total
    # y le tenemos que pasar los indices
    circle_gpu = pipeline.vertex_list_indexed(DEFINITION+1, GL_TRIANGLES, create_circle_indices())

    # Copiamos los datos, añadimos el color
    circle_gpu.position[:] = circle_pos
    circle_gpu.color[:] = circle_col

    @window.event
    def on_draw():

        # Esta linea limpia la pantalla entre frames
        window.clear()
        glClearColor(0.1, 0.1, 0.1, 0.0)

        with pipeline as _:
            circle_gpu.draw(GL_TRIANGLES)

    
    pyglet.app.run()

    
