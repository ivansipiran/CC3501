import trimesh as tm
import pyglet
import numpy as np
from pyglet.gl import *
import os
import sys
sys.path.append(os.path.dirname((os.path.dirname(__file__))))
import grafica.transformations as tr


WIDTH = 600
HEIGHT = 600

window = pyglet.window.Window(WIDTH, HEIGHT, "Auxiliar 3")

def file_to_vertexlist(path, color, pipeline):
    mesh = tm.load(path, process = False)
    #aplicamos un scale y una traslación para asegurarnos
    #que el modelo cabe en la pantalla y que está al centro
    mesh.apply_transform(tr.uniformScale(
        2.0 / mesh.scale) @ tr.translate(*-mesh.centroid))
    
    vertex_list = tm.rendering.mesh_to_vertexlist(mesh)

    #en la posicion [0] esta la cantidad de vertices
    #en [3] estan los indices
    buffer = pipeline.vertex_list_indexed(vertex_list[0], GL_TRIANGLES, vertex_list[3])
    
    #en [4][1] estan los vertices
    buffer.position = vertex_list[4][1]

    buffer.color = color * vertex_list[0]

    return buffer


if __name__ == "__main__":
    
    vertex_source = """
#version 330

in vec3 position;
in vec3 color;

uniform float intensity;
uniform mat4 transform;

out vec3 fragColor;

void main() {
    fragColor = color * intensity;
    gl_Position = transform * vec4(position, 1.0f);
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

    cow = file_to_vertexlist(__file__ + "/../assets/cow.obj", [1, 1, 1], pipeline)
    rat = file_to_vertexlist(__file__ + "/../assets/rat.obj", [0, 1, 0], pipeline)

    #para transform
    theta = np.pi/4

    @window.event
    def on_draw():

        glClearColor(0.1, 0.1, 0.1, 0.0)
        
        window.clear()

        pipeline.use()

        pipeline["intensity"] = 0.5

        transform = tr.rotationY(theta)
        transform = np.reshape(transform, (16, 1), order="F")
        pipeline["transform"] = transform
        cow.draw(GL_TRIANGLES)
        

    #P3 2.
    def update(dt):
        global theta
        theta += 0.05

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()

    

    
    
