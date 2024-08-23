import pyglet
from OpenGL import GL
import numpy as np
# importamos las librerias ^


# Opcionalmente seteamos variables para el tamaño
WIDTH = 640
HEIGHT = 640

# controlador de la ventana, basicamente una ventana
class Controller(pyglet.window.Window):
    #Función init se ejecuta al construir el objeto
    def __init__(self, title, *args, **kargs):
        super().__init__(*args, **kargs)
        # Evita error cuando se redimensiona a 0
        self.set_minimum_size(240, 240)
        self.set_caption(title)

    # Por ahora no queremos actualizar nada aquí
    def update(self, dt):
        pass


# programa principal
if __name__ == "__main__":
    # creamos una instancia del controlador
    controller = Controller("Auxiliar 0", width=WIDTH,
                            height=HEIGHT, resizable=True)

    # A continuación se encuentra el vertex shader
    # Este programa corre una vez por cada vertice 
    # Recibe:   un vector posición de 2 dimensiones
    #           un vector color de 3 dimensiones
    #           un float con la intensidad del vertice
    # 
    # Entrega:  un vector de 3 dimensiones con el color
    #           un vector intensidad con la intensidad            
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
    # Se ejecuta un vez sobre cada pixel
    # Entrega: un vector de 4 dimensiones que define el color del pixel (r, g, b, a)
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
    frag_shader = pyglet.graphics.shader.Shader(
        fragment_source_code, "fragment")
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
        1, 0.5, 1
    ], dtype=np.float32)

    # Ahora asignamos lo que definimos a la figura:
    # Aquí prueben cambiar GL_TRIANGLES por GL_LINE_LOOP
    gpu_triangle = pipeline.vertex_list(3, GL.GL_LINE_LOOP)
    gpu_triangle.position = positions
    gpu_triangle.color = colors
    gpu_triangle.intensity = intensities

    # Esta función se llama más abajo
    def update(dt):
        # podrían probar colocando algo aqui...
        #print("test")
        pass
        

    @controller.event
    def on_draw():
        # color de fondo al limpiar un frame (0,0,0) es negro
        GL.glClearColor(0, 0, 0, 1.0)
        # si hay algo dibujado se limpia del frame
        controller.clear()
        # se le dice al pipeline que se va a usar
        pipeline.use()

        # Aquí prueben cambiar GL_TRIANGLES por GL_LINE_LOOP
        gpu_triangle.draw(GL.GL_LINE_LOOP)

    # Como dice la documentación:
    # The schedule_interval method causes a function to be called every “n” seconds: 
    # schedule_interval(function, n)
    pyglet.clock.schedule_interval(update, 1/60)

    # Esta función recibe opcionalmente la frecuencia en que se actualiza la pantalla
    # por defecto es 1/60 pero podrían cambiarla: pyglet.app.run(1/120)
    pyglet.app.run()
