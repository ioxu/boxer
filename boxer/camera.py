'''
camera object
'''
import pyglet
import pyglet.gl as gl
import pyglet.math
from pyglet.window import mouse
import math
import boxer.shaping


class Camera(pyglet.event.EventDispatcher):
    def __init__(self, window : pyglet.window.Window,
                position : pyglet.math.Vec2 = pyglet.math.Vec2(0.0, 0.0)):
        print("starting %s"%self)

        self.window : pyglet.window.Window = window
        #self.position : pyglet.math.Vec2 = position
        #self.position : pyglet.math.Vec2 = property( self.get_position, self.set_position )
        #self.position = property( self.get_position, self.set_position )
        self.transform : pyglet.math.Mat4 = pyglet.math.Mat4()

        self.enabled = True

        # zoom
        self.zoom : float =  1.0
        self.zoom_rate : float = 0.1#0.02
        self.zoom_min : float = 0.01
        self.zoom_max : float = 6.0
        self.last_zoom : float = 1.0
        # pan
        self.is_panning = False

        #pyglet.clock.schedule_interval(self.update, 1/144.0)
        self.global_time : float = 0.0

        # start with a centered camera
        self.reset()


    def as_json(self) -> dict:
        return {
            "transform": self.transform,
            "position": self.get_position(),
            "zoom": self.zoom,
        }


    def enable(self) -> None:
        self.enabled = True


    def disable(self) -> None:
        self.enabled = False


    def reset(self) -> None:
        """
        reset the camera zoom and translation to be centered on the origin of the worksheet
        """
        window_size = self.window.get_size()
        print("camera.window.size = %s"%str(window_size))
        self.zoom = 1.0
        self.transform = pyglet.math.Mat4.from_translation( pyglet.math.Vec3( window_size[0]/2.0, window_size[1]/2.0 , 0.0) )


    def push(self) -> None:
        self.window.view = self.transform @ pyglet.math.Mat4().from_scale( pyglet.math.Vec3(2.0, 1.0, 1.0) )


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


    def set_position(self, pos : pyglet.math.Vec3):
        """
        set the position of the camera        
        """
        #self.transform.column(3) = (pos.x, pos.y, pos.z, pos.w)
        #self.transform.column[3]
        raise NotImplementedError


    position = property( get_position, set_position )


    def on_mouse_motion(self,  x, y, dx, dy ):
        #if self.enabled:
        pass


    def on_mouse_release(self, x, y, buttons, modifiers):
        if self.enabled:
            if buttons & mouse.MIDDLE:
                self.is_panning = False


    def on_mouse_press(self, x, y, buttons, modifiers):
        if self.enabled:
            if buttons & mouse.MIDDLE:
                self.is_panning = True


    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers ):
        """
        camera pan on middle-mouse drag
        # TODO : camera zoom on right-mouse drag
        """
        if self.enabled:
            if buttons & mouse.MIDDLE:
                self.transform = self.transform@pyglet.math.Mat4.from_translation(
                    pyglet.math.Vec3(dx * (1/self.zoom) , dy * (1/self.zoom), 0.0) )

                self.dispatch_event("transform_changed", self.transform)


    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        """
        camera zoom on mouse scroll
        """
        if self.enabled:
            zoom_dt = 1 + scroll_y * self.zoom_rate
            # if the delta takes zoom outside the limits,
            # then just use the last zoom amount rather than 
            # clamp at the limit, because I can't work out how
            # to keep the delta synchronised with the amount that
            # the new zoom is over the limit in terms of a proportion of delta
            self.last_zoom = self.zoom
            update_zoom = self.zoom * zoom_dt
            if update_zoom > self.zoom_max or update_zoom < self.zoom_min:
                self.zoom = self.last_zoom
                zoom_dt = 1.0
            else:
                self.zoom *= zoom_dt

            # transforms
            offset = pyglet.math.Vec3( x, y, 0.0 )
            offset_t = pyglet.math.Mat4.from_translation( -offset )
            scaled_t = pyglet.math.Mat4.from_scale( pyglet.math.Vec3( zoom_dt, zoom_dt, 1.0 ) )
            reoffset_t = pyglet.math.Mat4.from_translation( offset )
            self.transform =reoffset_t @ scaled_t @ offset_t @ self.transform 
            
            self.dispatch_event("transform_changed", self.transform)


    def start(self) -> None:
        """declare camera ready to use"""
        self.dispatch_event("transform_changed", self.transform)


# matrix things:
# https://math.stackexchange.com/questions/237369/given-this-transformation-matrix-how-do-i-decompose-it-into-translation-rotati

# events
Camera.register_event_type("transform_changed")
