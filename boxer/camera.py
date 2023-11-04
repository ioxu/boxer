'''
camera object
'''
import pyglet
import pyglet.gl as gl
import pyglet.math
import math

class Camera(object):
    def __init__(self, window : pyglet.window.Window,
                position : pyglet.math.Vec2 = pyglet.math.Vec2(0.0, 0.0)):
        print("starting %s"%self)

        self.window = window
        self.position = position
        self.global_time = 0.0

        pyglet.clock.schedule_interval(self.update, 1/144.0)

        print("window.view : %s"%str(self.window.view))


    def push(self) -> None:
        self.window.view = self.window.view.from_translation(pyglet.math.Vec3(self.position.x, self.position.y, 0.0))


    def pop(self) -> None:
        self.window.view = pyglet.math.Mat4()


    def update(self, delta) -> None:
        self.global_time += delta

        speed = 0.3
        mag = 200.0

        self.position.x = math.sin( self.global_time * speed ) * mag
        self.position.y = math.cos( self.global_time * speed ) * mag

