import numpy as np
from OpenGL.GL import glEnable, glDisable, glBindTexture, GL_TRIANGLES, GL_CULL_FACE, GL_TEXTURE_2D, GL_CLAMP_TO_EDGE, GL_LINEAR
from PIL import Image
from grafica.textures import texture_2D_setup
import grafica.transformations as tr

class Texture():
    def __init__(self,
                 path=None,
                 image=None,
                 sWrapMode=GL_CLAMP_TO_EDGE,
                 tWrapMode=GL_CLAMP_TO_EDGE,
                 minFilterMode=GL_LINEAR,
                 maxFilterMode=GL_LINEAR,
                 flip_top_bottom=True):
        self.texture = None
        self.sWrapMode = sWrapMode
        self.tWrapMode = tWrapMode
        self.minFilterMode = minFilterMode
        self.maxFilterMode = maxFilterMode
        self.flip_top_bottom = flip_top_bottom

        if path is not None:
            self.create_from_file(path)
        elif image is not None:
            self.create_from_image(image)
        else:
            image = Image.fromarray(np.array([[[255, 255, 255, 255]]], dtype=np.uint8))
            self.create_from_image(image)
            

    def create_from_image(self, image):
        self.texture = texture_2D_setup(image, self.sWrapMode, self.tWrapMode, self.minFilterMode, self.maxFilterMode, self.flip_top_bottom)

    def create_from_file(self, path):
        image = Image.open(path)
        self.texture = texture_2D_setup(image, self.sWrapMode, self.tWrapMode, self.minFilterMode, self.maxFilterMode, self.flip_top_bottom)

    def bind(self):
        glBindTexture(GL_TEXTURE_2D, self.texture)

    def unbind(self):
        glBindTexture(GL_TEXTURE_2D, 0)

class DirectionalLight():
    def __init__(self, diffuse = [1, 1, 1], specular = [1, 1, 1], ambient = [0.1, 0.1, 0.1]):
        self.diffuse = np.array(diffuse, dtype=np.float32)
        self.specular = np.array(specular, dtype=np.float32)
        self.ambient = np.array(ambient, dtype=np.float32)

class PointLight():
    def __init__(self, diffuse = [1, 1, 1], specular = [1, 1, 1], ambient = [0.1, 0.1, 0.1], constant = 1.0, linear = 0.09, quadratic = 0.032):
        self.diffuse = np.array(diffuse, dtype=np.float32)
        self.specular = np.array(specular, dtype=np.float32)
        self.ambient = np.array(ambient, dtype=np.float32)
        self.constant = constant
        self.linear = linear
        self.quadratic = quadratic

class SpotLight():
    def __init__(self, diffuse = [1, 1, 1], specular = [1, 1, 1], ambient = [0.1, 0.1, 0.1], constant = 1.0, linear = 0.09, quadratic = 0.032, cutOff = 0.91, outerCutOff = 0.82):
        self.diffuse = np.array(diffuse, dtype=np.float32)
        self.specular = np.array(specular, dtype=np.float32)
        self.ambient = np.array(ambient, dtype=np.float32)
        self.constant = constant
        self.linear = linear
        self.quadratic = quadratic
        self.cutOff = cutOff
        self.outerCutOff = outerCutOff

class Model():
    def __init__(self, position_data, uv_data=None, normal_data=None, index_data=None):
        self.position_data = position_data
        self.uv_data = uv_data
        self.normal_data = normal_data

        self.index_data = index_data
        if index_data is not None:
            self.index_data = np.array(index_data, dtype=np.uint32)

        self.gpu_data = None

    def init_gpu_data(self, pipeline):

        size = len(self.position_data)
        count = 3

        if "texCoord" in pipeline.attributes:
            size += len(self.uv_data)
            count += 2

        if "normal" in pipeline.attributes:
            size += len(self.normal_data)
            count += 3

        if self.index_data is not None:
            self.gpu_data = pipeline.vertex_list_indexed(size // count, GL_TRIANGLES, self.index_data)
        else:
            self.gpu_data = pipeline.vertex_list(size // count, GL_TRIANGLES)
        
        self.gpu_data.position[:] = self.position_data
        if "texCoord" in pipeline.attributes:
            self.gpu_data.texCoord[:] = self.uv_data
        
        if "normal" in pipeline.attributes:
            self.gpu_data.normal[:] = self.normal_data

    def draw(self, mode = GL_TRIANGLES, cull_face=True):
        if cull_face:
            glEnable(GL_CULL_FACE)
        else:
            glDisable(GL_CULL_FACE)
        self.gpu_data.draw(mode)
        glEnable(GL_CULL_FACE)

class Material():
    def __init__(self, ambient=[1, 1, 1], diffuse=[0.1, 0.1, 0.1], specular=[1, 1, 1], shininess=32.0):
        self.ambient = np.array(ambient, dtype=np.float32)
        self.diffuse = np.array(diffuse, dtype=np.float32)
        self.specular = np.array(specular, dtype=np.float32)
        self.shininess = shininess