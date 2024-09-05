import trimesh as tm
import pyglet
import numpy as np
from pyglet.gl import *
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))
from pyglet.math import Mat4, Vec3
from auxiliares.utils.scene_graph import *
from auxiliares.utils import shapes

WIDTH = 1000
HEIGHT = 1000

#Controller
class Controller(pyglet.window.Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.time = 0.0

window = Controller(WIDTH, HEIGHT, "Aux 5")

def models_from_file(path, pipeline):
    geom = tm.load(path)
    meshes = []
    if isinstance(geom, tm.Scene):
        for m in geom.geometry.values():
            meshes.append(m)
    else:
        meshes = [geom]

    models = []
    for m in meshes:
        m.apply_scale(2.0 / m.scale)
        m.apply_translation([-m.centroid[0], 0, -m.centroid[2]])
        vlist = tm.rendering.mesh_to_vertexlist(m)
        models.append(GameModel(vlist[4][1], vlist[3], pipeline))

    return models


#A. Defina las clases
class GameModel:
    pass

class Mesh():
    pass


if __name__ == "__main__":
    
    #Corregir el shader para que funcione con los uniforms del grafo de escena
    #u_color y u_model
    vertex_source = """
#version 330
in vec3 position;

uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;

void main() {
    gl_Position = projection * view * model * vec4(position, 1.0f);
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

    #Se define el pipeline
    vert_program = pyglet.graphics.shader.Shader(vertex_source, "vertex")
    frag_program = pyglet.graphics.shader.Shader(fragment_source, "fragment")
    pipeline = pyglet.graphics.shader.ShaderProgram(vert_program, frag_program)


    #B. Utilizando Mesh() defina la vaca y sphere
    

    # C. Haga el grafo para la escena dada
    graph = SceneGraph()
 

    #Matriz perspectiva
    pipeline["projection"] = Mat4.perspective_projection(WIDTH/HEIGHT, 0.01, 100, 90)
    #Camara estática en (0, 1, -0.5) que mira hacia el (0, 1, 1)
    pipeline["view"] = Mat4.look_at(Vec3(0, 1, -.5), Vec3(0, 1, 1), Vec3(0, 1, 0))


    @window.event
    def on_draw():
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glClearColor(0.1, 0.1, 0.1, 0.0)
        
        window.clear()

        pipeline.use()

        #Dibuje el grafo


    
    def update(dt):
        #Pasa el tiempo
        window.time += dt

        #Incluya aquí el movimiento
        
        
    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()

    

    
    
