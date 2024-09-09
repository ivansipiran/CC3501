import pyglet
from pyglet.gl import *
from pyglet.math import Mat4, Vec3
from pyglet.window import Window
from pyglet.graphics.shader import Shader, ShaderProgram
import trimesh as tm
import numpy as np


class Controller(Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.time = 0.0

window = Controller(800, 800, "Auxiliar 4")


class GameModel:
    def __init__(self, size, vertices, indices, pipeline) -> None:
        self.color = np.zeros(3, dtype=np.float32)
        self.position = np.zeros(3, dtype=np.float32)
        self.scale = np.ones(3, dtype=np.float32)
        self.rotation = np.zeros(3, dtype=np.float32)
        self._buffer = pipeline.vertex_list_indexed(size, GL_TRIANGLES, indices);
        self._buffer.position = vertices

    def model(self):
        translation = Mat4.from_translation(Vec3(*self.position))
        rotation = Mat4.from_rotation(self.rotation[0], Vec3(1, 0, 0)).rotate(self.rotation[1], Vec3(0, 1, 0)).rotate(self.rotation[2], Vec3(0, 0, 1))
        scale = Mat4.from_scale(Vec3(*self.scale))
        return translation @ rotation @ scale

    def draw(self):
        self._buffer.draw(GL_TRIANGLES)

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

if __name__ == "__main__":
    vsource = """
#version 330
in vec3 position;

uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;

void main() {
    gl_Position = projection * view * model * vec4(position, 1.0f);
}
    """

    fsource = """
#version 330
out vec4 outColor;

uniform vec3 color;

void main() {
    outColor = vec4(color, 1.0f);
}
    """

    pipeline = ShaderProgram(Shader(vsource, "vertex"), Shader(fsource, "fragment"))
    cow = models_from_file(__file__ + "/../../../assets/cow.obj", pipeline)[0]
    cow.color = [.8, .8, .8]
    cow.position = [-1, 0, -1]
    cow.rotation[1] = np.pi / 4

    rat = models_from_file(__file__ + "/../../../assets/rat.obj", pipeline)[0]
    rat.color = [.3, .3, .3]
    rat.scale = [.3] * 3
    rat.position = [1, 0, 1]
    rat.rotation[1] = -np.pi / 2

    leaves, tree = models_from_file(__file__ + "/../../../assets/tree.obj", pipeline)
    leaves.color = [0, .7, .3]
    leaves.scale = [3] * 3
    tree.color = [.5, .3, .0]
    tree.scale = [3] * 3

    floor = GameModel(4, [.5, .5, 0, .5, -.5, 0, -.5, -.5, 0, -.5, .5, 0], [0, 1, 2, 2, 3, 0], pipeline)
    floor.color = [0, .4, .1]
    floor.rotation[0] = np.pi / 2
    floor.scale = [100] * 3

    scene = [cow, rat, tree, leaves, floor]


    @window.event
    def on_draw():
        window.clear()
        glClearColor(0, .6, .8, 1)
        glEnable(GL_DEPTH_TEST)
        with pipeline:
            pipeline["view"] = Mat4.look_at(Vec3(0, 1, 3), Vec3(0, 1, 0), Vec3(0, 1, 0))
            pipeline["projection"] = Mat4.perspective_projection(window.aspect_ratio, 1, 10, 90)
            for m in scene:
                pipeline["color"] = m.color
                pipeline["model"] = m.model()
                m.draw()

    pyglet.app.run() 
    
