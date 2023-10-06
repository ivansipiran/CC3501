from networkx import DiGraph, edge_dfs
from OpenGL.GL import GL_TRIANGLES
import grafica.transformations as tr
import numpy as np

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
                 mode=GL_TRIANGLES,
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
