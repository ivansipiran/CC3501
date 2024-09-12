from pyglet.graphics.shader import ShaderProgram, Shader
import trimesh as tm
from OpenGL.GL import GL_LINES, GL_TRIANGLES
import os
from pathlib import Path
from auxiliares.utils.drawables import Model, Texture
from trimesh.scene.scene import Scene
from auxiliares.utils.scene_graph import SceneGraph 
import auxiliares.utils.shapes as shapes

import grafica.transformations as tr

def get_path(path):
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), path)

def init_axis(controller):
    with open(Path(os.path.dirname(__file__)) / "../shaders/transform.vert") as f:
        color_vertex_source_code = f.read()

    with open(Path(os.path.dirname(__file__)) / "../shaders/color.frag") as f:
        color_fragment_source_code = f.read()

    color_pipeline = ShaderProgram(Shader(color_vertex_source_code, "vertex"), Shader(color_fragment_source_code, "fragment"))

    axes = Model(shapes.Axes["position"])
    # axes.init_gpu_data()

    axis_scene = SceneGraph(controller)
    axis_scene.add_node("axes", attach_to="root", mesh=axes, pipeline=color_pipeline, mode=GL_LINES)

    axis_scene["axes"]["mesh"].gpu_data.color[:] = shapes.Axes["color"]

    return axis_scene

def init_pipeline(vertex_source, fragment_source):
    with open(vertex_source) as f:
        vs = f.read()

    with open(fragment_source) as f:
        fs = f.read()

    pipeline = ShaderProgram(
        Shader(vs, "vertex"),
        Shader(fs, "fragment")
    )

    return pipeline

def mesh_from_file(path):
    mesh_data = tm.load(path)
    mesh_data.apply_transform(tr.uniformScale(2.0 / mesh_data.scale) @ tr.translate(*-mesh_data.centroid))

    mesh_list = []

    def process_geometry(id, geometry):
        vertex_data = tm.rendering.mesh_to_vertexlist(geometry)
        indices = vertex_data[3]
        positions = vertex_data[4][1]
        uvs = None
        texture = None
        normals = vertex_data[5][1]

        if geometry.visual.kind == "texture":
            texture = Texture()
            uvs = vertex_data[6][1]
            texture.create_from_image(geometry.visual.material.image)

        model = Model(positions, uvs, normals, indices)
        return {"id": id, "mesh": model, "texture": texture}

    if type(mesh_data) is Scene:
        for id, geometry in mesh_data.geometry.items():
            mesh_list.append(process_geometry(id, geometry))
    else:
        mesh_list.append(process_geometry("model", mesh_data))

    return mesh_list
