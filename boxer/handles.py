import pyglet
import boxer

DEBUG_SHAPE_COLOR = (255, 80, 20, 128)
DEBUG_HIT_SHAPE_COLOR = (255, 240, 20, 20)


class Handle():
    
    def __init__(self,
        position : pyglet.math.Vec2 = pyglet.math.Vec2(),
        debug : bool = False,
        mouse : boxer.mouse.Mouse = None,
        batch : pyglet.graphics.Batch = None,
        group : pyglet.graphics.Group = None
        ):

        self.position = position
        self.mouse = mouse or None
        self.hilighted = False
        self.debug : bool = debug
        self.batch = batch or None
        self.group = group or None


    def is_inside(self, position : pyglet.math.Vec2 = pyglet.math.Vec2() ) -> bool:
        raise NotImplementedError()


    def upddate_position() -> None:
        raise NotImplementedError()


    def draw(self) -> None:
        if self.batch:
            self.batch.draw()
        if self.debug:
            self.draw_debug()


    def draw_debug(self) -> None:
        """immediate draw stuff if self.debug = True"""
        raise NotImplementedError()


    def on_mouse_motion(self, x, y, ds, dy):
        raise NotImplementedError()


    def on_mouse_press(self, x, y, buttons, modifiers):
        raise NotImplementedError()


    def on_mouse_release(self, x, y, buttons, modifiers):
        raise NotImplementedError()


    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers ):
        raise NotImplementedError()


class PointHandle( Handle ):
    def __init__(self,
        position : pyglet.math.Vec2 = pyglet.math.Vec2(),
        mouse : boxer.mouse.Mouse = None,
        debug : bool = False,
        hit_radius : float = 15.0,
        display_radius : float = 5.0,
        color = (255, 255, 90, 255),
        color_hover = (255, 255, 255, 255),
        batch : pyglet.graphics.Batch = None,
        group : pyglet.graphics.Group = None
        ):
        
        Handle.__init__(self,
            position = position,
            mouse = mouse,
            debug = debug,
            batch = batch,
            group = group)
        
        self.hit_radius : float = hit_radius
        self.display_radius : float = display_radius

        # dictionary?
        self._shapes = {}
        self._shapes["display"] = pyglet.shapes.Circle( self.position.x, self.position.y, radius=self.display_radius, segments=32, color=DEBUG_SHAPE_COLOR, batch=self.batch)
        self._shapes["hit"] = pyglet.shapes.Circle( self.position.x, self.position.y, radius=self.hit_radius, segments=32, color=DEBUG_HIT_SHAPE_COLOR, batch=self.batch)
        self._shapes["highlight"] = boxer.shapes.Arc( self.position.x, self.position.y, radius=self.hit_radius+1, segments=32, color=(255,255,255), batch=self.batch )
        self._shapes["highlight"].opacity = 20
        self._shapes["select"] = boxer.shapes.Arc( self.position.x, self.position.y, radius=self.hit_radius+3, segments=32, color=(255,70,70), batch=self.batch )
        self._shapes["select"].opacity = 20

    def draw_debug(self):
        pyglet.shapes.Circle( self.position.x, self.position.y, radius=self.hit_radius, color=DEBUG_HIT_SHAPE_COLOR).draw()
        pyglet.shapes.Circle( self.position.x, self.position.y, radius=self.display_radius, color=DEBUG_SHAPE_COLOR).draw()
  

    def is_inside( self, position : pyglet.math.Vec2 = pyglet.math.Vec2() ) -> bool:
        return  position.distance( self.position ) < self.hit_radius


    def on_mouse_press( self, x, y, buttons, modifiers ):
        if self.hilighted and buttons & pyglet.window.mouse.LEFT:
            self.selected = True
            self._shapes["select"].opacity = 220
        else:
            self.selected = False
            self._shapes["select"].opacity = 0


    def on_mouse_release( self, x, y, buttons, modifiers ):
        if self.hilighted and buttons & pyglet.window.mouse.LEFT:
            self.selected = False
            self._shapes["select"].opacity = 0
        else:
            self.selected = False
            self._shapes["select"].opacity = 0


    def on_mouse_drag( self, x, y, dx, dy, buttons, modifiers):
        if self.selected:
            # TODO: camera info!! be class method for converting spaces
            # OR ask mouse for works-space conversion (mouse holds a camera transform)
            self.position += pyglet.math.Vec2(dx, dy)*(1.0/self.mouse.camera_zoom) 
            self.update_position()


    def on_mouse_motion( self, x, y, dx, dy):
        if not self.mouse.captured_by_ui:
            wmp = self.mouse.world_position
            if self.is_inside( pyglet.math.Vec2( wmp.x, wmp.y ) ):
                self.hilighted = True
            else:
                self.hilighted = False

        if self.hilighted:
            self._shapes["highlight"].opacity = 120
        else:
            self._shapes["highlight"].opacity = 10


    def update_position( self ) -> None:
        self._shapes["display"].x = self.position.x
        self._shapes["display"].y = self.position.y
        self._shapes["hit"].x = self.position.x
        self._shapes["hit"].y = self.position.y
        self._shapes["highlight"].x = self.position.x
        self._shapes["highlight"].y = self.position.y
        self._shapes["select"].x = self.position.x
        self._shapes["select"].y = self.position.y