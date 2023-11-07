'''
camera object
'''
import pyglet
import pyglet.gl as gl
import pyglet.math
from pyglet.window import mouse
import math
import boxer.shaping


class Camera(object):
    def __init__(self, window : pyglet.window.Window,
                position : pyglet.math.Vec2 = pyglet.math.Vec2(0.0, 0.0)):
        print("starting %s"%self)

        self.window : pyglet.window.Window = window
        self.position : pyglet.math.Vec2 = position
        
        self.transform = pyglet.math.Mat4()

        # zoom
        self.zoom : float =  1.0
        self.zoom_rate : float = 0.1#0.02
        self.zoom_centre_x : float = 0.0
        self.zoom_centre_y : float = 0.0
        self.zoom_offset_x : float = 0.0
        self.zoom_offset_y : float = 0.0
        self.last_zoom : float = 1.0
        # pan
        self.is_panning = False

		# mouse position
        self.mouse_pos_x : float = 0.0
        self.mouse_pos_y : float = 0.0
        self.mouse_pos_dx : float = 0.0
        self.mouse_pos_dy : float = 0.0

        #pyglet.clock.schedule_interval(self.update, 1/144.0)
        self.global_time : float = 0.0
        #print("window.view : %s"%str(self.window.view))


    def push(self) -> None:
        # cam_translation : pyglet.math.Mat4 = pyglet.math.Mat4.from_translation(pyglet.math.Vec3(self.position.x, self.position.y, 0.0))
        # cam_zoom : pyglet.math.Mat4 = pyglet.math.Mat4.from_scale( pyglet.math.Vec3( self.zoom, self.zoom, 1.0 ) )
        # self.window.view = cam_zoom@cam_translation

        self.window.view = self.transform


    def pop(self) -> None:
        self.window.view = pyglet.math.Mat4()


    # def update(self, delta) -> None:
    #     self.global_time += delta
    #     speed = 0.75
    #     mag = 200.0
    #     self.zoom = boxer.shaping.remap( math.sin( self.global_time * 10.0 + 0.7542 ) , -1.0, 1.0, 0.95, 1.05)
    #     self.position.x = math.sin( self.global_time * speed ) * mag
    #     self.position.y = math.cos( self.global_time * speed ) * mag


    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers ):
        """
        camera pan on middle-mouse drag
        TODO : camera zoom on right-mouse drag
        """
        #print("mouse.on_mouse_drag %s"%buttons)
        #print("panning %s %s"%(x,y) )
        if buttons & mouse.MIDDLE:
            self.mouse_pos_x = x
            self.mouse_pos_y = y
            self.mouse_pos_dx = dx
            self.mouse_pos_dy = dy

            # self.update_position( self.position.x + self.mouse_pos_dx * (1/self.zoom) ,
            #                     self.position.y + self.mouse_pos_dy * (1/self.zoom) )
            # self.is_panning = True

            # transform
            self.transform = self.transform@pyglet.math.Mat4.from_translation(
                pyglet.math.Vec3(self.mouse_pos_dx * (1/self.zoom) , self.mouse_pos_dy * (1/self.zoom), 0.0) )
            self.is_panning = True


    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        """
        camera zoom on mouse scroll
        """
        #zz = self.zoom + scroll_y * self.zoom_rate * self.zoom

        zz = 1 + scroll_y * self.zoom_rate

        print(zz, self.zoom)
        self.zoom = min(max(0.05,self.zoom * zz),10)
        #self.transform = self.transform@pyglet.math.Mat4.scale( pyglet.math.Vec3(self.zoom, self.zoom, 1.0) ) #.from_scale( pyglet.math.Vec3(self.zoom, self.zoom, 1.0) )
        self.transform = self.transform.scale( (zz, zz, 1.0) )


    def update_position(self, x, y ):
        self.position.x = x
        self.position.y = y
