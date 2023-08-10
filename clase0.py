import pyglet
from pyglet.window import key

class Controller(pyglet.window.Window):
    def __init__(self, width, height, title="Pyglet window"):
        super().__init__(width, height, title)
        self.x = 0
        self.total_time = 0.0
       
controller = Controller(width=1280, height=800)
label = pyglet.text.Label('Hola CG 2023', font_name='Times New Roman', font_size=36, 
                            x=controller.x, y=controller.height//2, anchor_x='left', anchor_y='center')
image = pyglet.resource.image('assets/boo.png')

@controller.event
def on_draw():
    controller.clear()
    label.draw()
    image.blit(controller.x, 100)

@controller.event
def on_key_press(symbol, modifiers):
    if symbol == key.RIGHT:
        controller.x = controller.x + 10
        label.x = controller.x        
    elif symbol == key.LEFT:
        controller.x = controller.x - 10
        label.x = controller.x
    elif symbol == key.ESCAPE:
        controller.close()

def update(dt, controller):
    controller.x += 1
    label.x = controller.x
    
pyglet.clock.schedule_interval(update, 1/60, controller)
pyglet.app.run()