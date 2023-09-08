import networkx as nx
import os
import sys
from itertools import chain
from pathlib import Path

import numpy as np
import pyglet
import pyglet.gl as GL
import trimesh as tm
import matplotlib.cm as cm
# importamos esta función de trimesh porque nos permitirá asignarle una propiedad a cada vértice
# y pintaremos el conejo en función de esa propiedad
# en este caso, es la curvatura de la superficie
from trimesh.curvature import discrete_gaussian_curvature_measure

if sys.path[0] != "":
    sys.path.insert(0, "")
sys.path.append('../../')

import grafica.transformations as tr

def create_solar_system(mesh):
    graph = nx.DiGraph(root='sun')

    graph.add_node("sun", transform=tr.identity())
    graph.add_node("sun_geometry", mesh=mesh, transform=tr.uniformScale(0.8), color=np.array((1.0, 0.73,0.03)))
    graph.add_edge("sun", "sun_geometry")

    graph.add_node("earth", transform=tr.translate(2.5, 0.0, 0.0))
    graph.add_node("earth_geometry", mesh=mesh, transform=tr.uniformScale(0.3), color=np.array((0.0, 0.59, 0.78)))

    graph.add_edge("sun", "earth")
    graph.add_edge("earth", "earth_geometry")

    graph.add_node("moon", transform=tr.translate(0.5, 0.0, 0.0))
    graph.add_node("moon_geometry", mesh=mesh, transform=tr.uniformScale(0.1), color=np.array((0.3, 0.3, 0.3)))

    graph.add_edge("earth", "moon")
    graph.add_edge("moon", "moon_geometry")

    return graph

def create_simple_solar(mesh):
    graph = nx.DiGraph(root='sun')

    graph.add_node("sun", transform=tr.identity())
    graph.add_node("sun_geometry", mesh=mesh, transform=tr.uniformScale(2.0), color=np.array((1.0, 0.73,0.03)))
    graph.add_edge("sun", "sun_geometry")

    return graph

if __name__ == "__main__":
    width = 960
    height = 960

    try:
        config = pyglet.gl.Config(sample_buffers=1, samples=4)
        window = pyglet.window.Window(960, 960, config=config)
    except pyglet.window.NoSuchConfigException:
        window = pyglet.window.Window(960, 960)

    sphere = tm.load("../../assets/sphere.off")

    with open(Path(os.path.dirname(__file__)) / "mesh_vertex_shader.glsl") as f:
        vertex_source_code = f.read()

    with open(Path(os.path.dirname(__file__)) / ".." / "hello_world" / "fragment_program.glsl") as f:
        fragment_source_code = f.read()

    vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_shader = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
    solar_pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

    sphere_vertex_list = tm.rendering.mesh_to_vertexlist(sphere)
    sphere_gpu = solar_pipeline.vertex_list_indexed(len(sphere_vertex_list[4][1]) // 3, GL.GL_TRIANGLES, sphere_vertex_list[3])
    sphere_gpu.position[:] = sphere_vertex_list[4][1]
    print(len(sphere_vertex_list[4][1]))

    graph = create_solar_system(sphere_gpu)

    # agregamos la vista y la proyección a nuestro estado de programa
    window.program_state = {
        # al conejo le aplicamos la identidad por ahora.
        "scene_graph": graph,
        "total_time": 0.0,
        # transformación de la vista
        "view": tr.lookAt(
            np.array([5, 5, 5]),  # posición de la cámara
            np.array([0, 0, 0]),  # hacia dónde apunta
            np.array([0.0, 1.0, 0.0]),  # vector para orientarla (arriba)
        ),
        # transformación de proyección, en este caso, en perspectiva
        "projection": tr.perspective(60, width / height, 0.001, 100.0),
    }

    @window.event
    def on_draw():
        GL.glClearColor(0.5, 0.5, 0.5, 1.0)
        GL.glLineWidth(1.0)
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)

        window.clear()

        # lo activamos a la hora de graficar nuestra escena
        GL.glEnable(GL.GL_DEPTH_TEST)

        # hora de dibujar al conejo! activamos su shader
        solar_pipeline.use()
        solar_pipeline["view"] = window.program_state["view"].reshape(16, 1, order="F")
        solar_pipeline["projection"] = window.program_state["projection"].reshape(16, 1, order="F")

        graph = window.program_state["scene_graph"]

        root_key = graph.graph["root"]
        edges = list(nx.edge_dfs(graph, source=root_key))
        
        transformations = {root_key: graph.nodes[root_key]["transform"]}

        for src, dst in edges:
            current_node = graph.nodes[dst]

            if not dst in transformations:
                dst_transform = current_node["transform"]
                transformations[dst] = transformations[src] @ dst_transform

            if "mesh" in current_node:
                if "color" in current_node:
                    solar_pipeline["color"] = current_node["color"]
                
                trans = transformations[dst]
                solar_pipeline["transform"] = trans.reshape(16,1,order='F')
                current_node["mesh"].draw(GL.GL_TRIANGLES)

    def update_solar_system(dt, window):
        window.program_state["total_time"] += dt
        total_time = window.program_state["total_time"]

        graph = window.program_state["scene_graph"]

        graph.nodes["earth"]["transform"] = tr.rotationY(2*total_time)@tr.translate(2.5, 0.0, 0.0)
        graph.nodes["moon"]["transform"] = tr.rotationY(3*total_time)@tr.translate(0.5, 0.0, 0.0)

    pyglet.clock.schedule_interval(update_solar_system, 1 / 60.0, window)
    pyglet.app.run(1 / 60.0)