import pyglet           # pip install pyglet
from OpenGL import GL   # pip install PyOpenGL
import numpy as np      # pip install numpy o conda install numpy

WIDTH = 640
HEIGHT = 640

class Controller(pyglet.window.Window):
    def __init__(self, title, *args, **kargs):
        super().__init__(*args, **kargs)
        self.set_minimum_size(240, 240) # Evita error cuando se redimensiona a 0
        self.set_caption(title)

    def update(self, dt):
        pass

if __name__ == "__main__":
    # Instancia del controller
    controller = Controller("Auxiliar 1", width=WIDTH, height=HEIGHT, resizable=True)
    
    # Código del vertex shader
    # cada vértice tiene 3 atributos
    # posición (x, y)
    # color (r, g, b)
    # intensidad
    vertex_source_code = """
        #version 330

        in vec2 position;
        in vec3 color;
        in float intensity;

        out vec3 fragColor;
        out float fragIntensity;

        void main()
        {
            fragColor = color;
            fragIntensity = intensity;
            gl_Position = vec4(position, 0.0f, 1.0f);
        }
    """

    # Código del fragment shader
    # La salida es un vector de 4 componentes (r, g, b, a)
    # donde a es la transparencia (por ahora no nos importa, se deja en 1)
    # El color resultante de cada fragmento ("pixel") es el color del vértice multiplicado por su intensidad
    fragment_source_code = """
        #version 330

        in vec3 fragColor;
        in float fragIntensity;
        out vec4 outColor;

        void main()
        {
            outColor = fragIntensity * vec4(fragColor, 1.0f);
        }
    """

    # Compilación de shaders
    vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_shader = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
    # Creación del pipeline
    pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

    # Posición de los vértices de un triángulo
    # 3 vértices con 2 coordenadas (x, y)
    # donde (0, 0) es el centro de la pantalla
    positions = np.array([
        -0.5, -0.5,
         0.5, -0.5, 
         0.0,  0.5
    ], dtype=np.float32)

    # Colores de los vértices del triángulo
    # 3 vértices con 3 componentes (r, g, b)
    colors = np.array([
        1, 0, 0,
        0, 1, 0,
        0, 0, 1
    ], dtype=np.float32)

    # Intensidad de los vértices del triángulo
    # 3 vértices con 1 componente (intensidad)
    intensities = np.array([
        1, 0.5, 0
    ], dtype=np.float32)

    # Creación de los vértices del triángulo para uso en gpu
    gpu_triangle = pipeline.vertex_list(3, GL.GL_TRIANGLES)
    gpu_triangle.position = positions
    gpu_triangle.color = colors
    gpu_triangle.intensity = intensities

    # Análogo al triángulo
    # Se define un cuadrado del tamaño de la pantalla
    quad_positions = np.array([
        -1, -1, # abajo izquierda
         1, -1, # abajo derecha
        -1,  1, # arriba izquierda
         1,  1  # arriba derecha
    ], dtype=np.float32)

    quad_colors = np.array([
        1, 0, 0,
        0, 1, 0,
        0, 0, 1,
        1, 1, 1
    ], dtype=np.float32)

    quad_intensities = np.array([1, 1, 1, 1], dtype=np.float32)

    # Índices de los vértices del cuadrado
    # 2 triángulos con 3 vértices cada uno (ver ppt del auxiliar 1, slide 13)
    quad_indices = np.array([
        0, 1, 2,
        1, 3, 2
    ], dtype=np.uint32)

    # Creación de los vértices del cuadrado para uso en gpu
    # A diferencia del triángulo, aquí se usan los índices definidos anteriormente
    gpu_quad = pipeline.vertex_list_indexed(4, GL.GL_TRIANGLES, quad_indices)
    gpu_quad.position = quad_positions
    gpu_quad.color = quad_colors
    gpu_quad.intensity = quad_intensities

    # draw loop
    # la función on_draw se ejecuta cada vez que se quiere dibujar algo en pantalla
    @controller.event
    def on_draw():
        # color de fondo al limpiar un frame (0,0,0) es negro
        GL.glClearColor(0, 0, 0, 1.0)
        # si hay algo dibujado se limpia del frame
        controller.clear()
        # se le dice al pipeline que se va a usar
        pipeline.use()
         # se le entrega al pipeline los vértices del cuadrado
         # queremos que estos se dibujen (draw) como un triángulo (GL_TRIANGLES)
        gpu_quad.draw(GL.GL_TRIANGLES)
        # triángulo, análogo al cuadrado
        # se dibuja después que el cuadrado ya que si se dibuja antes no se vería porque el cuadrado es más grande
        gpu_triangle.draw(GL.GL_TRIANGLES)

    pyglet.clock.schedule_interval(controller.update, 1/60) # se ejecuta update del controller cada 1/60 segundos
    pyglet.app.run() # se ejecuta pyglet