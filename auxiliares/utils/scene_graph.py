from networkx import DiGraph, edge_dfs
from OpenGL.GL import GL_TRIANGLES
import grafica.transformations as tr
import numpy as np
from auxiliares.utils.drawables import DirectionalLight, PointLight, SpotLight, Texture

class SceneGraph():
    def __init__(self, controller=None):
        self.graph = DiGraph(root="root")
        self.add_node("root")
        self.controller = controller
        self.num_point_lights = 0
        self.num_spot_lights = 0
        self.transformations = {}

    def add_node(self,
                 name,
                 attach_to="root",
                 mesh=None,
                 pipeline=None,
                 light=None,
                 color=[1, 1, 1],
                 material=None,
                 texture=None,
                 transform=tr.identity(),
                 position=[0, 0, 0],
                 rotation=[0, 0, 0],
                 scale=[1, 1, 1],
                 mode=GL_TRIANGLES,
                 cull_face=True):
        if pipeline is None and mesh is not None:
            raise ValueError("Definir pipeline para un mesh")
        
        if pipeline is None and light is not None:
            raise ValueError("Definir pipeline para una luz")
        
        _texture = texture
        if mesh is not None:
            mesh.init_gpu_data(pipeline)
            if texture is None:
                _texture = Texture()

        if light is not None and isinstance(light, PointLight):
            if self.num_point_lights == 16:
                raise ValueError("No se pueden agregar más de 16 PointLights")
            self.num_point_lights += 1

        if light is not None and isinstance(light, SpotLight):
            if self.num_spot_lights == 16:
                raise ValueError("No se pueden agregar más de 16 SpotLights")
            self.num_spot_lights += 1

        self.graph.add_node(
            name, 
            mesh=mesh,
            light=light,
            pipeline=pipeline,
            color=color,
            material=material,
            texture=_texture,
            transform=transform,
            position=np.array(position, dtype=np.float32),
            rotation=np.array(rotation, dtype=np.float32),
            scale=np.array(scale, dtype=np.float32),
            mode=mode,
            cull_face=cull_face)
        
        self.graph.add_edge(attach_to, name)

    def remove_node(self, name):
        if name in self.graph.nodes:
            self.graph.remove_node(name)

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
        rotation_matrix =  tr.rotationY(node["rotation"][1]) @ tr.rotationX(node["rotation"][0]) @ tr.rotationZ(node["rotation"][2])
        scale_matrix = tr.scale(node["scale"][0], node["scale"][1], node["scale"][2])
        return transform @ translation_matrix @ rotation_matrix @ scale_matrix

    def get_forward(self, node):
        node = self.graph.nodes[node]
        rotation_matrix = tr.rotationY(node["rotation"][1]) @ tr.rotationX(node["rotation"][0]) @ tr.rotationZ(node["rotation"][2])
        return rotation_matrix @ np.array([0, 0, 1, 0], dtype=np.float32)

    def draw(self):
        root_key = self.graph.graph["root"]
        edges = list(edge_dfs(self.graph, source=root_key))
        self.transformations = {root_key: self.get_transform(root_key)}
        pointLightIndex = 0
        spotLightIndex = 0

        for src, dst in edges:
            current_node = self.graph.nodes[dst]

            if not dst in self.transformations:
                self.transformations[dst] = self.transformations[src] @ self.get_transform(dst)

            current_pipeline = current_node["pipeline"]
            if current_pipeline is None:
                continue

            """ 
            Setup de luces 
            """
            if current_node["light"] is not None:
                current_pipelines = current_pipeline
                if not isinstance(current_pipeline, list):
                    current_pipelines = [current_pipeline]

                for pipeline in current_pipelines:
                    pipeline.use()
                    if "u_viewPos" in pipeline.uniforms:
                        pipeline["u_viewPos"] = self.controller.program_state["camera"].position[:3]
                    if isinstance(current_node["light"], DirectionalLight):
                        if "u_dirLight.direction" in pipeline.uniforms:
                            pipeline["u_dirLight.direction"] = (self.transformations[src] @ self.get_forward(dst))[:3]
                            pipeline["u_dirLight.ambient"] = current_node["light"].ambient
                            pipeline["u_dirLight.diffuse"] = current_node["light"].diffuse
                            pipeline["u_dirLight.specular"] = current_node["light"].specular
                    elif isinstance(current_node["light"], PointLight):
                        if "u_numPointLights" in pipeline.uniforms:
                            pipeline["u_numPointLights"] = self.num_point_lights
                            position = (self.transformations[src] @ np.array([current_node["position"][0], current_node["position"][1], current_node["position"][2], 1], dtype=np.float32))[:3]
                            pipeline[f"u_pointLights[{str(pointLightIndex)}].position"] = position
                            pipeline[f"u_pointLights[{str(pointLightIndex)}].ambient"] = current_node["light"].ambient
                            pipeline[f"u_pointLights[{str(pointLightIndex)}].diffuse"] = current_node["light"].diffuse
                            pipeline[f"u_pointLights[{str(pointLightIndex)}].specular"] = current_node["light"].specular
                            pipeline[f"u_pointLights[{str(pointLightIndex)}].constant"] = current_node["light"].constant
                            pipeline[f"u_pointLights[{str(pointLightIndex)}].linear"] = current_node["light"].linear
                            pipeline[f"u_pointLights[{str(pointLightIndex)}].quadratic"] = current_node["light"].quadratic

                    elif isinstance(current_node["light"], SpotLight):
                        if "u_numSpotLights" in pipeline.uniforms:
                            pipeline["u_numSpotLights"] = self.num_spot_lights
                            position = (self.transformations[src] @ np.array([current_node["position"][0], current_node["position"][1], current_node["position"][2], 1], dtype=np.float32))[:3]
                            pipeline[f"u_spotLights[{str(spotLightIndex)}].position"] = position
                            pipeline[f"u_spotLights[{str(spotLightIndex)}].direction"] = (self.transformations[src] @ self.get_forward(dst))[:3]
                            pipeline[f"u_spotLights[{str(spotLightIndex)}].ambient"] = current_node["light"].ambient
                            pipeline[f"u_spotLights[{str(spotLightIndex)}].diffuse"] = current_node["light"].diffuse
                            pipeline[f"u_spotLights[{str(spotLightIndex)}].specular"] = current_node["light"].specular
                            pipeline[f"u_spotLights[{str(spotLightIndex)}].constant"] = current_node["light"].constant
                            pipeline[f"u_spotLights[{str(spotLightIndex)}].linear"] = current_node["light"].linear
                            pipeline[f"u_spotLights[{str(spotLightIndex)}].quadratic"] = current_node["light"].quadratic
                            pipeline[f"u_spotLights[{str(spotLightIndex)}].cutOff"] = current_node["light"].cutOff
                            pipeline[f"u_spotLights[{str(spotLightIndex)}].outerCutOff"] = current_node["light"].outerCutOff

                if isinstance(current_node["light"], PointLight):
                    pointLightIndex += 1
                elif isinstance(current_node["light"], SpotLight):
                    spotLightIndex += 1

                continue

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

            if current_node["mesh"] is not None:
                """
                Setup de Material
                """
                if "u_color" in current_pipeline.uniforms:
                    current_pipeline["u_color"] = np.array(current_node["color"], dtype=np.float32)

                if "u_material.diffuse" in current_pipeline.uniforms:
                    material = current_node["material"]
                    if material is None:
                        raise ValueError("Material es None")
                    current_pipeline["u_material.diffuse"] = material.diffuse
                    current_pipeline["u_material.ambient"] = material.ambient
                    current_pipeline["u_material.specular"] = material.specular
                    current_pipeline["u_material.shininess"] = material.shininess

                textured = "u_texture" in current_pipeline.uniforms and current_node["texture"] is not None
                if textured:
                    current_node["texture"].bind()

                """
                Setup de Mesh
                """                
                current_pipeline["u_model"] = np.reshape(self.transformations[dst], (16, 1), order="F")
                current_node["mesh"].draw(current_node["mode"], current_node["cull_face"])

                if textured:
                    current_node["texture"].unbind()
            
    def find_position(self, node_name):
        for src, dst in self.transformations.items():
            if src == node_name:
                return dst[:3, 3]
        return None