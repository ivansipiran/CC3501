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
    dx = 16/atlas.width
    dy = 16/atlas.height
    return [
    dx*xoffset, dy*yoffset,
    dx*(xoffset+1), dy*yoffset,
    dx*(xoffset+1), dy*(yoffset+1),
    dx*xoffset, dy*(yoffset+1) ]

if __name__ == "__main__":

    controller = Controller(800,600,"Auxiliar 6")
    controller.set_exclusive_mouse(True)

    vert_source = """
#version 330

in vec3 position;
in vec2 texCoord;

uniform mat4 u_model = mat4(1.0);
uniform mat4 u_view = mat4(1.0);
uniform mat4 u_projection = mat4(1.0);

out vec2 fragTexCoord;

void main() {
    fragTexCoord = texCoord;
    gl_Position = u_projection * u_view * u_model * vec4(position, 1.0f);
}
    """
    frag_source = """
#version 330

in vec2 fragTexCoord;

out vec4 outColor;

uniform sampler2D u_texture;

void main() {
    outColor =  texture(u_texture, fragTexCoord);
}
    """

    pipeline = ShaderProgram(Shader(vert_source, "vertex"), Shader(frag_source, "fragment"))

    cam = MyCam([-2,0,0])

    axis = init_axis(cam)

    tworld = SceneGraph(cam)
    world = SceneGraph(cam)

    # parte A
    zorzal = mesh_from_file("assets/zorzal.obj")
    world.add_node("zorzal_root")
    for m in zorzal:
        world.add_node(m["id"],attach_to="zorzal_root", mesh=m["mesh"], pipeline=pipeline, texture=m["texture"])

    # parte B
    quad = Model(shapes.Square["position"], shapes.Square["uv"], index_data=shapes.Square["indices"])
    tworld.add_node("tree", mesh=quad, pipeline=pipeline, texture=Texture("assets/tree.png"), position=[2, 1.5, 2], scale=[2, 3, 1], cull_face=False)

    # parte C
    atlas = Texture("assets/atlas.png",minFilterMode=GL_NEAREST, maxFilterMode=GL_NEAREST)
    my_uv = [
        # Cara frontal
        *get_atlas_uv(27,20,atlas),
        # Cara trasera
        *get_atlas_uv(27,20,atlas),
        # Cara izquierda
        *get_atlas_uv(27,20,atlas),
        # Cara derecha
        *get_atlas_uv(27,20,atlas),
        # Cara superior
        *get_atlas_uv(28,18,atlas),
        # Cara inferior
        *get_atlas_uv(23,23,atlas)]
    box = Model(shapes.Cube["position"], my_uv, index_data=shapes.Cube["indices"])
    world.add_node("dice", mesh=box, pipeline=pipeline, texture=atlas, position=[0, 1, -2], scale=[.5, .5, .5])


    @controller.event
    def on_draw():
        controller.clear()
        glClearColor(1,1,1,1)
        glEnable(GL_DEPTH_TEST)
        # pueden cambiar el orden de visualización y ver que pasa
        axis.draw()
        world.draw()
        glEnable( GL_BLEND )
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        tworld.draw()
        glDisable( GL_BLEND )

    @controller.event
    def on_key_press(symbol, modifiers):
        if symbol == key.SPACE: controller.light_mode = True

        if controller.light_mode:
            cam.direction = np.zeros(2)
        else:
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
        if symbol == key.SPACE: controller.light_mode = False
        if controller.light_mode:
            cam.direction = np.zeros(2)
        else:
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

        # parte A
        t_pos = tworld.find_position("tree")
        c_pos = cam.position.copy()
        c_pos[1] = 0
        dir = t_pos - c_pos

        tworld["tree"]["rotation"][1] = np.arctan(-dir[2]/ dir[0]) + np.pi/2

        controller.time += dt

    clock.schedule_interval(update,1/60)
    run()

