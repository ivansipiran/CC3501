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


# Definimos la clase "Imagen" para generar imagenes mas facilmente
class Image():
    def __init__(self, path, width, height, x = 0, y = 0):
        self.image = pyglet.resource.image(path)
        self.image.width = width
        self.image.height = height
        self.x = x
        self.y = y

    def draw(self):
        self.image.blit(self.x, self.y)

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

    # Definimos la imagen, con su tamaño y su posicion
    cow = Image("assets/cow.png", 200, 200, 0, HEIGHT/2 - 150/2)

    # Función llamada cada "frame" depende de schedule_interval()
    def update(dt):
        # Controlamos el cambio de posición de la imagen en cada frame
        velocity = 5
        cow.x += velocity
        if cow.x >= WIDTH: 
            cow.x = -cow.image.width


    # Función llamada cada frame
    @controller.event
    def on_draw():
        # color de fondo al limpiar un frame (0,0,0) es negro
        GL.glClearColor(0, 0, 0, 1.0)
        # si hay algo dibujado se limpia del frame
        controller.clear()
        # se le dice al pipeline que se va a usar
        pipeline.use()

        # Dibujamos la imagen
        cow.draw()

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()
