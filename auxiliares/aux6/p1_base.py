from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.window import Window, key
from pyglet.gl import *
from pyglet.app import run
from pyglet import math
from pyglet import clock

import sys, os
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))
from auxiliares.utils.helpers import init_axis, mesh_from_file
from auxiliares.utils.camera import FreeCamera
from auxiliares.utils.scene_graph import SceneGraph
from auxiliares.utils import shapes
from auxiliares.utils.drawables import Texture, Model

class Controller(Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.time = 0
        self.light_mode = False

class MyCam(FreeCamera):
    def __init__(self, position=np.array([0, 0, 0]), camera_type="perspective"):
        super().__init__(position, camera_type)
        self.direction = np.array([0,0,0])
        self.speed = 2

    def time_update(self, dt):
        self.update()
        dir = self.direction[0]*self.forward + self.direction[1]*self.right
        dir_norm = np.linalg.norm(dir)
        if dir_norm:
            dir /= dir_norm
        self.position += dir*self.speed*dt
        self.focus = self.position + self.forward

def get_atlas_uv(xoffset, yoffset, atlas):
    size = 16
    deltax = 16 / atlas.width
    deltay = 16 / atlas.height

    return [
        deltax*xoffset, deltay*yoffset,
        deltax*(xoffset+1), deltay*yoffset,
        deltax*(xoffset+1), deltay*(yoffset+1),
        deltax*xoffset, deltay*(yoffset+1)
    ]

if __name__ == "__main__":

    controller = Controller(800,600,"Auxiliar 6")
    controller.set_exclusive_mouse(True)

    vert_source = """
#version 330

in vec3 position;
in vec2 texCoord;

out vec2 fragTexCoord;

uniform mat4 u_model = mat4(1.0);
uniform mat4 u_view = mat4(1.0);
uniform mat4 u_projection = mat4(1.0);

void main() {
    fragTexCoord = texCoord;
    gl_Position = u_projection * u_view * u_model * vec4(position, 1.0f);
}
    """
    frag_source = """
#version 330
in vec2 fragTexCoord;

uniform sampler2D u_texture;

out vec4 outColor;

void main() {
    outColor = texture(u_texture, fragTexCoord);
}
    """

    pipeline = ShaderProgram(Shader(vert_source, "vertex"), Shader(frag_source, "fragment"))

    cam = MyCam([-2,0,0])

    axis = init_axis(cam)

    world = SceneGraph(cam)
    tworld = SceneGraph(cam)

    zorzal = mesh_from_file("assets/zorzal.obj")

    world.add_node("zorzal_core")
    for d in zorzal:
        world.add_node(d["id"], attach_to="zorzal_core", mesh=d["mesh"], texture=d["texture"], pipeline=pipeline)

    quad = Model(shapes.Square["position"], shapes.Square["uv"], index_data=shapes.Square["indices"])

    tworld.add_node("billboard", mesh=quad, texture=Texture("assets/Tree.png"), pipeline=pipeline, cull_face=False)

    tworld["billboard"]["position"] = [0, 1, -5]
    tworld["billboard"]["scale"] = [1, 2, 1]

    atlas = Texture("assets/atlas.png", minFilterMode=GL_NEAREST, maxFilterMode=GL_NEAREST)
    my_uv = [
        *get_atlas_uv(18, 29, atlas),
        *get_atlas_uv(18, 29, atlas),
        *get_atlas_uv(18, 29, atlas),
        *get_atlas_uv(18, 29, atlas),
        *get_atlas_uv(18, 28, atlas),
        *get_atlas_uv(23, 25, atlas),
    ]
    cube = Model(shapes.Cube["position"], my_uv, index_data=shapes.Cube["indices"])

    world.add_node("diamond", mesh=cube, texture=atlas, pipeline=pipeline)
    world["diamond"]["position"] = [5, 0, 0]
    world["diamond"]["scale"] = [.5, .5, .5]

    @controller.event
    def on_draw():
        controller.clear()
        glClearColor(1,1,1,1)
        glEnable(GL_DEPTH_TEST)
        axis.draw()
        world.draw()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        tworld.draw()
        glDisable(GL_BLEND)

    @controller.event
    def on_key_press(symbol, modifiers):
        if symbol == key.W:
            cam.direction[0] = 1
        if symbol == key.S:
            cam.direction[0] = -1

        if symbol == key.A:
            cam.direction[1] = 1
        if symbol == key.D:
            cam.direction[1] = -1

    @controller.event
    def on_key_release(symbol, modifiers):
        if symbol == key.W or symbol == key.S:
            cam.direction[0] = 0

        if symbol == key.A or symbol == key.D:
            cam.direction[1] = 0

    @controller.event
    def on_mouse_motion(x, y, dx, dy):
        cam.yaw += dx * .001
        cam.pitch += dy * .001
        cam.pitch = math.clamp(cam.pitch, -(np.pi/2 - 0.01), np.pi/2 - 0.01)

    def update(dt):
        world.update()
        tworld.update()
        axis.update()
        cam.time_update(dt)

        t_pos = tworld.find_position("billboard")
        c_pos = cam.position.copy()
        c_pos[1] = 0
        dir = c_pos - t_pos
        dir /= np.linalg.norm(dir)

        tworld["billboard"]["rotation"][1] = np.arctan(-dir[2] / dir[0]) - np.pi/2

        controller.time += dt

    clock.schedule_interval(update,1/60)
    run()

