'''
camera object
'''
import pyglet
import pyglet.gl as gl
import pyglet.math
import math
import boxer.shaping


class Camera(object):
    def __init__(self, window : pyglet.window.Window,
                position : pyglet.math.Vec2 = pyglet.math.Vec2(0.0, 0.0)):
        print("starting %s"%self)

        self.window : pyglet.window.Window = window
        self.position : pyglet.math.Vec2 = position
        self.global_time : float = 0.0
        self.zoom : float =  1.0

        pyglet.clock.schedule_interval(self.update, 1/144.0)

        #print("window.view : %s"%str(self.window.view))


    def push(self) -> None:
        #cam_translation : pyglet.math.Mat4 = pyglet.math.Mat4.from_translation(pyglet.math.Vec3(self.position.x, self.position.y, 0.0))
        cam_translation : pyglet.math.Mat4 = pyglet.math.Mat4.from_translation(pyglet.math.Vec3(200.0, 200.0, 0.0))
        #cam_zoom : pyglet.math.Mat4 = pyglet.math.Mat4.from_scale( pyglet.math.Vec3( self.zoom ) )
        cam_zoom : pyglet.math.Mat4 = pyglet.math.Mat4.from_scale( pyglet.math.Vec3( self.zoom, self.zoom, 1.0 ) )
        #self.window.view = self.window.view.from_translation(pyglet.math.Vec3(self.position.x, self.position.y, 0.0))
        
        
        #self.window.view = cam_translation@cam_zoom
        self.window.view = cam_zoom@cam_translation


    def pop(self) -> None:
        self.window.view = pyglet.math.Mat4()


    def update(self, delta) -> None:
        self.global_time += delta

        speed = 0.75
        mag = 200.0

        self.zoom = boxer.shaping.remap( math.sin( self.global_time * 10.0 + 0.7542 ) , -1.0, 1.0, 0.95, 1.05)

        self.position.x = math.sin( self.global_time * speed ) * mag
        self.position.y = math.cos( self.global_time * speed ) * mag
