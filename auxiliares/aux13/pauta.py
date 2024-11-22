from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.window import Window, key
from pyglet.gl import *
from pyglet.app import run
import math
from pyglet import clock
import sys, os
import numpy as np
import trimesh as tm

from pyglet import math as ma

sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))
from auxiliares.utils.helpers import init_axis, init_pipeline, mesh_from_file
from auxiliares.utils.camera import FreeCamera
from auxiliares.utils.scene_graph import SceneGraph
from auxiliares.utils.drawables import Model, DirectionalLight, Material

class Controller(Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.time = 0
        self.sky_color = np.array([0.2, 0.3, 0.5])
        self.intensity = 0.1
        self.light_mode = False
        self.light_dir = np.zeros(2)
        self.light_color = np.ones(3)
        self.light_distance = 1

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
 



def bezier_surface(control_points, u_steps, v_steps):
    
    def bernstein_poly(i, n, t):
        return math.comb(n, i) * (t**i) * ((1 - t)**(n - i))
    
    def bernstein_poly_derivative(i, n, t):
        if n == 0:
            return 0
        if i == 0:
            return 1

        return math.comb(n - 1, i - 1) * (t**(i - 1)) * ((1 - t)**(n - i)) * i - \
               math.comb(n - 1, i) * (t**i) * ((1 - t)**(n - i - 1)) * (n - i)

    m, n, _ = control_points.shape
    u_values = np.linspace(0, 1, u_steps) #retorna un array de tamaño u_steps con numeros equitativamente espaciados del 0 al 1
    v_values = np.linspace(0, 1, v_steps)
    
    surface_points = []
    surface_normals = []

    for u in u_values:
        for v in v_values:
            # calcula  p(u, v) con la formula 
            point = np.zeros(3) #[0, 0, 0]
            du = np.zeros(3)
            dv = np.zeros(3)
            #son 2 sumatorias very costoso
            for i in range(m):
                for j in range(n):
                    #calculo punto
                    b_u = bernstein_poly(i, m - 1, u)
                    b_v = bernstein_poly(j, n - 1, v)

                    #calculo diferenciales (para la normal)
                    db_u = bernstein_poly_derivative(i, m - 1, u)
                    db_v = bernstein_poly_derivative(j, n - 1, v)

                    point += b_u * b_v * control_points[i, j]
                    du += db_u * b_v * control_points[i, j]
                    dv += b_u * db_v * control_points[i, j]

            #la normal es el producto cruz de ambos lados
            normal = np.cross(du, dv)
            if np.linalg.norm(normal) != 0:
                normal = normal / np.linalg.norm(normal)  #normalizar

            surface_points.append(point)
            surface_normals.append(normal)

    surface_points = np.array(surface_points)
    surface_normals = np.array(surface_normals)

    # Generación indices
    triangles = []
    for i in range(u_steps - 1):
        for j in range(v_steps - 1):
            p0 = i * v_steps + j
            p1 = p0 + 1
            p2 = (i + 1) * v_steps + j
            p3 = p2 + 1

            #dos triangulos por celda
            triangles.append([p0, p1, p2])
            triangles.append([p1, p3, p2])

    triangles = np.array(triangles)
    return surface_points.flatten(), surface_normals.flatten(), triangles.flatten()

# Example usage
control_points = np.array([
    [[0, 0, 0], [0, 1, 1], [0, 2, 0]],
    [[1, 0, 1], [1, 1, 2], [1, 2, 1]],
    [[2, 0, 0], [2, 1, 1], [2, 2, 0]]
])  # A 3x3 grid of control points

u_steps = 10  # Resolution in the u-direction
v_steps = 10  # Resolution in the v-direction

surface_points, surface_normals, triangles = bezier_surface(control_points, u_steps, v_steps)



if __name__ == "__main__":

    #controller/window
    controller = Controller(1000,1000,"Auxiliar 13")
    controller.set_exclusive_mouse(True)

    root = os.path.dirname(__file__)
    #pipeline con un flat shader
    flat_pipeline = init_pipeline(root + "/flat.vert", root + "/flat.frag") 
    #camara
    cam = MyCam([1,1,-5])

    surface = Model(surface_points, normal_data=surface_normals, index_data=triangles)

    world = SceneGraph(cam)

    # Agrego todos los objetos al grafo

    world.add_node("surface",
                   mesh=surface,
                   pipeline=flat_pipeline,
                   material=Material(ambient=[1, 0, 0])
                   )

    world.add_node("sun",
                   pipeline=flat_pipeline,
                   light=DirectionalLight(ambient=[.6, .6, .6], diffuse=[.6, .6, .6]),
                   rotation=[-np.pi/2, 0, 0]
                   )
    
    shark = mesh_from_file(root + "/shark.obj")[0]['mesh']

    world.add_node("shark",
                   mesh=shark,
                   pipeline=flat_pipeline,
                   material=Material([0.6, 0.5, 0.9]),
                   rotation=[-np.pi/2, np.pi/2, np.pi],
                   scale=[1.5, 1.5, 1.5],
                   position=[-1, 1, 0]
                   )

    def update(dt):
        
        world.update()
        
        cam.time_update(dt)

        controller.time += dt

        

    @controller.event
    def on_draw():
        controller.clear()
        glClearColor(0.1, 0.1, 0.1, 1)
        glEnable(GL_DEPTH_TEST)
        #glCullFace(GL_FRONT_AND_BACK)
        
        world.draw()

    @controller.event
    def on_key_press(symbol, modifiers):
        if symbol == key.SPACE: controller.light_mode = not controller.light_mode
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
        cam.pitch = ma.clamp(cam.pitch, -(np.pi/2 - 0.01), np.pi/2 - 0.01)

    @controller.event
    def on_mouse_scroll(x, y, scroll_x, scroll_y):
        controller.light_distance += scroll_y*.01

    clock.schedule_interval(update, 1/60)
    run()
