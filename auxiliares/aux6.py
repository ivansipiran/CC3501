import pyglet
from OpenGL import GL
from networkx import DiGraph, edge_dfs
import numpy as np
import sys

# No es necesario este bloque de código si se ejecuta desde la carpeta raíz del repositorio
# v
if sys.path[0] != "":
    sys.path.insert(0, "")
sys.path.append('../../')
# ^
# No es necesario este bloque de código si se ejecuta desde la carpeta raíz del repositorio

import grafica.transformations as tr
import auxiliares.utils.shapes as shapes
from auxiliares.utils.camera import FreeCamera
from auxiliares.utils.drawables import Model, Texture
from auxiliares.utils.helpers import init_axis, init_pipeline, mesh_from_file, get_path

WIDTH = 640
HEIGHT = 640

textured_lit_vertex_source = """
#version 330

in vec3 position;
in vec2 texCoord;
in vec3 normal;

uniform vec3 u_color = vec3(1.0);

uniform mat4 u_model = mat4(1.0);
uniform mat4 u_view = mat4(1.0);
uniform mat4 u_projection = mat4(1.0);

out vec3 fragColor;
out vec2 fragTexCoord;
out vec3 fragNormal;

void main()
{
    fragColor = u_color;
    fragTexCoord = texCoord;
    fragNormal = mat3(transpose(inverse(u_model))) * normal;
    
    gl_Position = u_projection * u_view * u_model * vec4(position, 1.0f);
}
"""

textured_lit_fragment_source = """
#version 330

in vec3 fragColor;
in vec2 fragTexCoord;
in vec3 fragNormal;

out vec4 outColor;

uniform sampler2D u_texture;
uniform vec3 u_lightDir;
uniform vec3 u_lightColor;

float AMBIENT = 0.15f;

float computeLight(vec3 normal, vec3 lightDir)
{
    float diffuse = max(dot(normal, lightDir), 0.0);
    return diffuse;
}

void main()
{
    vec3 normal = normalize(fragNormal);
    float diffuse = computeLight(normal, u_lightDir);
    vec4 texel = texture(u_texture, fragTexCoord);
    if (texel.a < 0.5)
        discard;
    vec4 color = vec4(fragColor, 1.0f) * texel * max(diffuse, AMBIENT);
    outColor = color * vec4(u_lightColor, 1.0f);
}
"""

class Controller(pyglet.window.Window):
    def __init__(self, title, *args, **kargs):
        super().__init__(*args, **kargs)
        self.set_minimum_size(240, 240) # Evita error cuando se redimensiona a 0
        self.set_caption(title)
        self.key_handler = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.key_handler)
        self.program_state = { "total_time": 0.0, "camera": None, "light": None }
        self.init()

    def init(self):
        GL.glClearColor(1, 1, 1, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        GL.glFrontFace(GL.GL_CCW)

    def is_key_pressed(self, key):
        return self.key_handler[key]

class SceneGraph():
    def __init__(self, controller=None):
        self.graph = DiGraph(root="root")
        self.add_node("root")
        self.controller = controller

    def add_node(self,
                 name,
                 attach_to="root",
                 mesh=None,
                 pipeline=None,
                 color=[1, 1, 1],
                 texture=None,
                 transform=tr.identity(),
                 position=[0, 0, 0],
                 rotation=[0, 0, 0],
                 scale=[1, 1, 1],
                 mode=GL.GL_TRIANGLES,
                 cull_face=True):
        if pipeline is None and mesh is not None:
            raise ValueError("Definir pipeline para un mesh")
        
        if mesh is not None:
            mesh.init_gpu_data(pipeline)

        self.graph.add_node(
            name, 
            mesh=mesh,
            pipeline=pipeline,
            color=color,
            texture=texture,
            transform=transform,
            position=np.array(position, dtype=np.float32),
            rotation=np.array(rotation, dtype=np.float32),
            scale=np.array(scale, dtype=np.float32),
            mode=mode,
            cull_face=cull_face)
        
        self.graph.add_edge(attach_to, name)

    def __getitem__(self, name):
        if name not in self.graph.nodes:
            raise KeyError(f"Node {name} not in graph")

        return self.graph.nodes[name]
    
    def __setitem__(self, name, value):
        if name not in self.graph.nodes:
            raise KeyError(f"Node {name} not in graph")

        self.graph.nodes[name] = value
    
    def get_transform(self, node):
        node = self.graph.nodes[node]
        transform = node["transform"]
        translation_matrix = tr.translate(node["position"][0], node["position"][1], node["position"][2])
        rotation_matrix = tr.rotationX(node["rotation"][0]) @ tr.rotationY(node["rotation"][1]) @ tr.rotationZ(node["rotation"][2])
        scale_matrix = tr.scale(node["scale"][0], node["scale"][1], node["scale"][2])
        return transform @ translation_matrix @ rotation_matrix @ scale_matrix

    def draw(self):
        root_key = self.graph.graph["root"]
        edges = list(edge_dfs(self.graph, source=root_key))
        transformations = {root_key: self.get_transform(root_key)}

        for src, dst in edges:
            current_node = self.graph.nodes[dst]

            if not dst in transformations:
                transformations[dst] = transformations[src] @ self.get_transform(dst)

            if current_node["mesh"] is not None:
                current_pipeline = current_node["pipeline"]
                current_pipeline.use()

                """ 
                Setup de cámara 
                """
                if "camera" in self.controller.program_state:
                    camera = self.controller.program_state["camera"]
                    if camera is None:
                        raise ValueError("Camera es None")
                    if "u_view" in current_pipeline.uniforms:
                        current_pipeline["u_view"] = camera.get_view()

                    if "u_projection" in current_pipeline.uniforms:
                        current_pipeline["u_projection"] = camera.get_projection()

                """ 
                Setup de luces 
                """
                lit = "u_lightDir" in current_pipeline.uniforms and "u_lightColor" in current_pipeline.uniforms and "light" in self.controller.program_state
                if lit:
                    light = self.controller.program_state["light"]
                    if light is None:
                        raise ValueError("Light es None")
                    current_pipeline["u_lightDir"] = light.direction[:3]
                    current_pipeline["u_lightColor"] = light.color

                """
                Setup de Meshes
                """
                current_pipeline["u_model"] = np.reshape(transformations[dst], (16, 1), order="F")

                if "u_color" in current_pipeline.uniforms:
                    current_pipeline["u_color"] = np.array(current_node["color"], dtype=np.float32)

                textured = "u_texture" in current_pipeline.uniforms and current_node["texture"] is not None
                if textured:
                    current_node["texture"].bind()

                current_node["mesh"].draw(current_node["mode"], current_node["cull_face"])

                if textured:
                    current_node["texture"].unbind()

class DirectionalLight():
    def __init__(self, direction = [0, 1, 0], color = [1, 1, 1]):
        self.direction = np.array([*direction, 1], dtype=np.float32)
        self.color = np.array(color, dtype=np.float32)

    def rotateX(self, angle):
        self.direction = tr.rotationX(angle) @ self.direction

    def rotateY(self, angle):
        self.direction = tr.rotationY(angle) @ self.direction


if __name__ == "__main__":
    # Instancia del controller
    controller = Controller("Auxiliar 6", width=WIDTH, height=HEIGHT, resizable=True)

    controller.program_state["camera"] = FreeCamera([1, 2, 2], "perspective")
    controller.program_state["camera"].yaw = -3* np.pi/ 4
    controller.program_state["camera"].pitch = -np.pi / 4

    controller.program_state["light"] = DirectionalLight()
    
    axis_scene = init_axis(controller)

    color_mesh_pipeline = init_pipeline(
        get_path("auxiliares/shaders/color_mesh.vert"),
        get_path("auxiliares/shaders/color_mesh.frag"))
    
    textured_mesh_pipeline = init_pipeline(
        get_path("auxiliares/shaders/textured_mesh.vert"),
        get_path("auxiliares/shaders/textured_mesh.frag"))
    
    lit_textured_mesh_pipeline = pipeline = pyglet.graphics.shader.ShaderProgram(
        pyglet.graphics.shader.Shader(textured_lit_vertex_source, "vertex"),
        pyglet.graphics.shader.Shader(textured_lit_fragment_source, "fragment"))

    cube = Model(shapes.Cube["position"], shapes.Cube["uv"], shapes.Cube["normal"], index_data=shapes.Cube["indices"])
    pyramid = Model(shapes.SquarePyramid["position"], shapes.SquarePyramid["uv"], shapes.SquarePyramid["normal"], index_data=shapes.SquarePyramid["indices"])
    triangle = Model(shapes.Triangle["position"], shapes.Triangle["uv"], shapes.Triangle["normal"])
    quad = Model(shapes.Square["position"], shapes.Square["uv"], shapes.Square["normal"], index_data=shapes.Square["indices"])

    textura = Texture("assets/bricks.jpg")
    textura2 = Texture("assets/boo.png", maxFilterMode=GL.GL_NEAREST)

    graph = SceneGraph(controller)
    graph.add_node("shapes")

    # mesh_from_file() devuelve una lista de diccionarios, cada uno con la información de un mesh
    # [{id, mesh, texture}, ...]
    zorzal = mesh_from_file("assets/zorzal.obj")
    for i in range(len(zorzal)):
        graph.add_node(zorzal[i]["id"],
                    attach_to="root",
                    mesh=zorzal[i]["mesh"],
                    pipeline=textured_mesh_pipeline,
                    texture=zorzal[i]["texture"],
                    cull_face=False)

    graph.add_node("cube",
                   attach_to="shapes",
                   mesh = cube,
                   pipeline = lit_textured_mesh_pipeline,
                   texture = textura,
                   position = [-2, 0, 0],
                   color = [1, 0, 0])
    graph.add_node("pyramid",
                     attach_to="shapes",
                     mesh = pyramid,
                     pipeline = lit_textured_mesh_pipeline,
                     texture=Texture(), # Textura vacía
                     position = [2, 0, 0],
                     color = [0, 1, 0])
    graph.add_node("triangle",
                    attach_to="shapes",
                    mesh = triangle,
                    pipeline = color_mesh_pipeline,
                    position = [0, 0, 2],
                    color = [0, 0, 1])
    graph.add_node("quad",
                    attach_to="shapes",
                    mesh = quad,
                    pipeline = textured_mesh_pipeline,
                    texture = textura2,
                    position = [0, 0, -2],
                    color = [1, 1, 1])
    
    def update(dt):
        controller.program_state["total_time"] += dt
        camera = controller.program_state["camera"]
        light = controller.program_state["light"]
        if controller.is_key_pressed(pyglet.window.key.A):
            camera.position -= camera.right * dt
        if controller.is_key_pressed(pyglet.window.key.D):
            camera.position += camera.right * dt
        if controller.is_key_pressed(pyglet.window.key.W):
            camera.position += camera.forward * dt
        if controller.is_key_pressed(pyglet.window.key.S):
            camera.position -= camera.forward * dt
        if controller.is_key_pressed(pyglet.window.key.Q):
            camera.position[1] -= dt
        if controller.is_key_pressed(pyglet.window.key.E):
            camera.position[1] += dt
        if controller.is_key_pressed(pyglet.window.key._1):
            camera.type = "perspective"
        if controller.is_key_pressed(pyglet.window.key._2):
            camera.type = "orthographic"
        camera.update()

        if controller.is_key_pressed(pyglet.window.key.UP):
            light.rotateX(-dt)
        if controller.is_key_pressed(pyglet.window.key.DOWN):
            light.rotateX(dt)
        if controller.is_key_pressed(pyglet.window.key.LEFT):
            light.rotateY(-dt)
        if controller.is_key_pressed(pyglet.window.key.RIGHT):
            light.rotateY(dt)

    @controller.event
    def on_resize(width, height):
        controller.program_state["camera"].resize(width, height)

    @controller.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        if buttons & pyglet.window.mouse.RIGHT:
            controller.program_state["camera"].yaw += dx * 0.01
            controller.program_state["camera"].pitch += dy * 0.01
        
        if buttons & pyglet.window.mouse.LEFT:
            graph["root"]["rotation"][0] += dy * 0.01
            graph["root"]["rotation"][1] += dx * 0.01


    # draw loop
    @controller.event
    def on_draw():
        controller.clear()
        axis_scene.draw()
        graph.draw()

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()
