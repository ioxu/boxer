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
        
        self.transform : pyglet.math.Mat4 = pyglet.math.Mat4()

        # zoom
        self.zoom : float =  1.0
        self.zoom_rate : float = 0.1#0.02
        self.zoom_min : float = 0.05
        self.zoom_max : float = 10.0


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

        # strat with a centered camera
        window_size = self.window.get_size()
        print("camera.window.size = %s"%str(window_size))
        self.transform = pyglet.math.Mat4.from_translation( pyglet.math.Vec3( window_size[0]/2.0, window_size[1]/2.0 , 0.0) )


    def push(self) -> None:
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


    def get_position(self) -> pyglet.math.Vec3:
        """
        get the position of the camera
        
        returns the translation straight from the camera's Mat4 transform
        """
        return self.transform.column(3)[:3]


    def on_mouse_motion(self,  x, y, dx, dy ):
        pass


    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers ):
        """
        camera pan on middle-mouse drag
        TODO : camera zoom on right-mouse drag
        """
        if buttons & mouse.MIDDLE:
            self.mouse_pos_x = x
            self.mouse_pos_y = y
            self.mouse_pos_dx = dx
            self.mouse_pos_dy = dy

            self.transform = self.transform@pyglet.math.Mat4.from_translation(
                pyglet.math.Vec3(self.mouse_pos_dx * (1/self.zoom) , self.mouse_pos_dy * (1/self.zoom), 0.0) )
            self.is_panning = True

            # print("self.position %s"%self.position)
            # print("self.transform origin %s"%str(self.transform.column(3)[:3]))


    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        """
        camera zoom on mouse scroll
        """
        zz = 1 + scroll_y * self.zoom_rate

        # limit zooming
        update_zoom = self.zoom * zz
        if update_zoom > self.zoom_max:
            self.zoom = self.zoom_max
            zz = 1.0
        elif update_zoom < self.zoom_min:
            self.zoom = self.zoom_min
            zz = 1.0
        else:
            self.zoom *= zz

        offset = pyglet.math.Vec3( x, y, 0.0 )
        offset_t = pyglet.math.Mat4.from_translation( -offset )
        scaled_t = pyglet.math.Mat4.from_scale( pyglet.math.Vec3( zz, zz, 1.0 ) )
        reoffset_t = pyglet.math.Mat4.from_translation( offset )
        self.transform =reoffset_t @ scaled_t @ offset_t @ self.transform 


# matrix things:
# https://math.stackexchange.com/questions/237369/given-this-transformation-matrix-how-do-i-decompose-it-into-translation-rotati

