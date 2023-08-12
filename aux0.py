import pyglet
from pyglet.window import key

WIDTH = 1280
HEIGHT = 720

class Controller(pyglet.window.Window):
    def __init__(self, title, *args, **kargs):
        super().__init__(*args, **kargs)
        self.set_minimum_size(320, 240)
        self.title = title
        self.set_caption(title)

class Text():
    def __init__(self, text):
        self.text = pyglet.text.Label(text,
            font_name='consolas',
            font_size=12, 
            x=controller.width//2,
            y=controller.height//2,
            anchor_x='center',
            anchor_y='center')

    def draw(self):
        self.text.draw()

    def set_position(self, x, y):
        self.text.x = x
        self.text.y = y

    def update(self, dt):
        pass


class Image():
    def __init__(self, path, width, height):
        self.image = pyglet.resource.image(path)
        self.image.width = width
        self.image.height = height
        self.x = 0
        self.y = 0

    def draw(self):
        self.image.blit(self.x, self.y)

    def update(self, dt):
        pass

    def resize(self, width, height):
        pass

class Dinosaur(Image):
    def __init__(self):
        super().__init__("assets/dinosaur.png", 100, 100)

    def update(self, dt):
        self.x += 1
        self.y -= 1
        if self.y <= 0:
            self.y = 0

class Background(Image):
    def __init__(self):
        super().__init__("assets/torres-del-paine-sq.jpg", WIDTH, HEIGHT)

    def resize(self, width, height):
        self.image.width = width
        self.image.height = height


controller = Controller("Ventana", width=WIDTH, height=HEIGHT, resizable=True)
dinosaur = Dinosaur()
background = Background()
text = Text("Estoy en el centro")
dragText = Text("Arrástrame")
    
@controller.event
def on_draw():
    controller.clear()
    background.draw()
    dinosaur.draw()
    text.draw()
    dragText.draw()

@controller.event
def on_key_press(symbol, modifiers):
    if symbol == key.SPACE:
        if modifiers & key.MOD_SHIFT:
            dinosaur.y += 100
        else:
            dinosaur.y += 50
    elif symbol == key.ESCAPE:
        controller.close()

@controller.event
def on_resize(width, height):
    background.resize(width, height)

@controller.event
def on_mouse_motion(x, y, dx, dy):
    controller.set_caption(f"{controller.title}, Mouse: ({x}, {y})")

@controller.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    if buttons & pyglet.window.mouse.LEFT:
        dragText.set_position(x, y)

def update(dt, controller):
    text.set_position(controller.width//2, controller.height//2)
    background.update(dt)
    dinosaur.update(dt)


pyglet.clock.schedule_interval(update, 1/60, controller)
pyglet.app.run()
