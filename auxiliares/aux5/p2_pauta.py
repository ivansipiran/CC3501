import trimesh as tm
import pyglet
import numpy as np
from pyglet.gl import *
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))
import grafica.transformations as tr
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
        models.append(GameModel(vlist[0], vlist[4][1], vlist[3], pipeline))

    return models


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

    
    vert_program = pyglet.graphics.shader.Shader(vertex_source, "vertex")
    frag_program = pyglet.graphics.shader.Shader(fragment_source, "fragment")
    pipeline = pyglet.graphics.shader.ShaderProgram(vert_program, frag_program)

    #Objeto base
    cube = GameModel(shapes.Cube["position"],shapes.Cube["indices"], pipeline)
    
    #Objetos faltantes con su transformación (conserve el scale)
    head = GameModel(shapes.Cube["position"],shapes.Cube["indices"], pipeline)
    head_model = Mat4.from_translation(Vec3(-0.2, 0.2, 0)) @ Mat4.from_scale(Vec3(0.35*0.2, 0.35*0.2, 0.35*0.2))

    chest = GameModel(shapes.Cube["position"],shapes.Cube["indices"], pipeline)
    chest_model = Mat4.from_translation(Vec3(0, 0.2, 0)) @ Mat4.from_scale(Vec3(0.5*0.2, 1*0.2, 0.35*0.2))

    arm = GameModel(shapes.Cube["position"],shapes.Cube["indices"], pipeline)
    arm_model = Mat4.from_translation(Vec3(0.2, 0.2, 0)) @ Mat4.from_scale(Vec3(0.2*0.2, 1*0.2, 0.2*0.2))

    #Grafo de escena
    graph = SceneGraph()
    graph.add_node("body", rotation=[0, np.pi + np.pi/4, 0], scale=[0.2, 0.2, 0.2], position=[0, 0, 0])
    #Añadimos el chest
    graph.add_node("chest",
                        attach_to="body",
                        mesh=cube,
                        pipeline=pipeline,
                        color=shapes.RED,
                        scale=[0.5, 1, 0.35]
                        )
    #Añadimos head
    graph.add_node("head",
                        attach_to="body",
                        mesh=cube,
                        pipeline=pipeline,
                        color=shapes.CYAN,
                        position=[0, 0.75, 0],
                        scale=[0.35, 0.35, 0.35]
                        )
    #Añádimos los brazos
    graph.add_node("left_arm",
                        attach_to="body",
                        mesh=cube,
                        pipeline=pipeline,
                        color=shapes.GREEN,
                        position=[-0.5, 0, 0],
                        rotation=[0, 0, -0.5],
                        scale=[0.2, 1, 0.2]
                        )
    graph.add_node("right_arm",
                        attach_to="body",
                        mesh=cube, 
                        color=shapes.GREEN,
                        pipeline=pipeline,
                        position=[0.5, 0, 0],
                        rotation=[0, 0, 0.5],
                        scale=[0.2, 1, 0.2],
                        )
    graph.add_node("left_leg", attach_to="body")
    graph.add_node("right_leg", attach_to="body")
    graph.add_node("left_upper_leg",
                            attach_to="left_leg",
                            mesh=cube, color=shapes.BLUE,
                            pipeline=pipeline,
                            position=[-0.2, -0.85, 0],
                            rotation=[0, 0, -0.15],
                            scale=[0.25, 0.75, 0.25],
                        )
    graph.add_node("right_upper_leg",
                            attach_to="right_leg",
                            mesh=cube, color=shapes.BLUE,
                            pipeline=pipeline,
                            position=[0.2, -0.85, 0],
                            rotation=[0, 0, 0.15],
                            scale=[0.25, 0.75, 0.25],
                        )
    graph.add_node("left_lower_leg",
                            attach_to="left_leg",
                            mesh=cube, color=shapes.DARK_BLUE,
                            pipeline=pipeline,
                            position=[-0.25, -1.5, 0],
                            scale=[0.2, 0.75, 0.2],
                        )
    graph.add_node("right_lower_leg",
                            attach_to="right_leg",
                            mesh=cube, color=shapes.DARK_BLUE,
                            pipeline=pipeline,
                            position=[0.25, -1.5, 0],
                            scale=[0.2, 0.75, 0.2],
                        )



    pipeline["projection"] = Mat4.perspective_projection(WIDTH/HEIGHT, 0.01, 100, 90)
    pipeline["view"] = Mat4.look_at(Vec3(0, 0, -.5), Vec3(0, 0, 0), Vec3(0, 1, 0))



    @window.event
    def on_draw():
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glClearColor(1, 1, 1, 0.0)
        
        window.clear()

        pipeline.use()

        graph.draw()

        #Uniforms de los objetos aislados
        #Ya no son necesarios ya que el grafo se encarga

        #pipeline["u_model"] = head_model
        #pipeline["u_color"] = shapes.CYAN
        #head.draw(GL_TRIANGLES)

        #pipeline["u_model"] = chest_model
        #pipeline["u_color"] = shapes.RED
        #chest.draw(GL_TRIANGLES)

        #pipeline["u_model"] = arm_model
        #pipeline["u_color"] = shapes.GREEN
        #arm.draw(GL_TRIANGLES)



    
    def update(dt):
        #Pasa el tiempo
        window.time += dt

        limb_rotation = np.sin(window.time * 5) / 2
        graph["left_arm"]["transform"] = tr.translate(0, 0.5, 0) @ tr.rotationX(limb_rotation) @ tr.translate(0, -0.5, 0)
        graph["right_arm"]["transform"] = tr.translate(0, 0.5, 0) @ tr.rotationX(-limb_rotation) @ tr.translate(0, -0.5, 0)
        graph["left_leg"]["transform"] = tr.translate(0, -0.5, 0) @ tr.rotationX(-limb_rotation) @ tr.translate(0, 0.5, 0)
        graph["right_leg"]["transform"] = tr.translate(0, -0.5, 0) @ tr.rotationX(limb_rotation) @ tr.translate(0, 0.5, 0)

        lower_limb_rotation = np.cos(window.time * 5) / 3
        graph["left_lower_leg"]["transform"] = tr.translate(0, -1.125, 0) @ tr.rotationX(lower_limb_rotation + 0.25) @ tr.translate(0, 1.125, 0)
        graph["right_lower_leg"]["transform"] = tr.translate(0, -1.125, 0) @ tr.rotationX(lower_limb_rotation + 0.25) @ tr.translate(0, 1.125, 0)


    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()

    

    
    
