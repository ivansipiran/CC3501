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
    def __init__(self, vertices, indices, pipeline) -> None:
        self.pipeline = pipeline
        
        self._buffer = pipeline.vertex_list_indexed(len(vertices)//3, GL_TRIANGLES, indices)
        self._buffer.position = vertices

    def draw(self, mode):
        self._buffer.draw(mode)

class Mesh():
    def __init__(self, path, pipeline):
        self.pipeline = pipeline

        self.buffer = models_from_file(path, pipeline)[0]

    def draw(self, mode):
        self.buffer.draw(mode)  


if __name__ == "__main__":
    #Corregir el shader para que funcione con los uniforms del grafo de escena
    #u_color y u_model
    vertex_source = """
#version 330

in vec3 position;
uniform vec3 u_color = vec3(1.0);


uniform mat4 u_model;
uniform mat4 view = mat4(1.0);
uniform mat4 projection = mat4(1.0);

out vec3 fragColor;

void main() {
    fragColor = u_color;
    gl_Position = projection * view * u_model * vec4(position, 1.0f);
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
    vaca_magica = Mesh(__file__ + "/../../../assets/cow.obj", pipeline)
    orb = Mesh(__file__ + "/../../../assets/sphere.obj", pipeline)

    # C. Haga el grafo para la escena dada
    graph = SceneGraph()

    #Nodo que contiene al resto
    graph.add_node("vaca_orbs", rotation=[0, np.pi/4, 0])

    #Vaca
    graph.add_node("vaca",
                   attach_to="vaca_orbs",
                   mesh=vaca_magica,
                   pipeline=pipeline,
                   color = [1, 1, 1])
    
    #Orbs
    graph.add_node("orb1",
                   attach_to="vaca_orbs",
                   mesh=orb,
                   pipeline=pipeline,
                   color = [1, 1, 0],
                   scale=[0.2, 0.2, 0.2])
    graph.add_node("orb2",
                   attach_to="vaca_orbs",
                   mesh=orb,
                   pipeline=pipeline,
                   color = [1, 1, 0],
                   scale=[0.2, 0.2, 0.2])
    graph.add_node("orb3",
                   attach_to="vaca_orbs",
                   mesh=orb,
                   pipeline=pipeline,
                   color = [1, 1, 0],
                   scale=[0.2, 0.2, 0.2])
    
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
        graph.draw()

    
    def update(dt):
        #Pasa el tiempo
        window.time += dt

        #Oscilación de arriba a abajo
        graph["vaca_orbs"]["position"] = [0, np.cos(window.time), 3]

        #Rotación de los orbs al rededor de la vaca
        graph["orb1"]["position"] = [np.cos(2*window.time), 0.5, np.sin(2*window.time)]
        graph["orb2"]["position"] = [0, 0.5 + np.cos(2*window.time), np.sin(2*window.time)]
        graph["orb3"]["position"] = [-np.cos(2*window.time), 0.5, -np.sin(2*window.time)]

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()

    

    
    
