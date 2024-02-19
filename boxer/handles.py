# ui handles (draggable areas)
import pyglet
import pyglet.gl as gl

if __name__ == "__main__":
    import sys
    sys.path.extend("..")

import boxer
import boxer.mouse
import boxer.shapes

DEBUG_SHAPE_COLOR = (255, 80, 20, 128)
DEBUG_HIT_SHAPE_COLOR = (255, 240, 20, 20)


class Handle(pyglet.event.EventDispatcher):
    
    SPACE_SCREEN = 0
    SPACE_WORLD = 1

    def __init__(self,
        name : str = "handle",
        position : pyglet.math.Vec2 = pyglet.math.Vec2(),
        debug : bool = False,
        space : int = SPACE_WORLD,
        mouse : boxer.mouse.Mouse = None,
        batch : pyglet.graphics.Batch = None,
        group : pyglet.graphics.Group = None,
        base_opacity : float = 1.0,
        highlighted_opacity : float = 1.0,
        selected_opacity : float = 1.0
        ):

        self.name = name
        if isinstance(position, tuple):
            position = pyglet.math.Vec2( position[0], position[1] )
        self.position = position
        self.mouse = mouse or None
        self.mouse_inside = False
        self.hilighted = False
        self.debug : bool = debug
        self.space : int = space
        self.batch = batch or pyglet.graphics.Batch()
        self.group = group or None
        self.base_opacity = base_opacity
        self.highlighted_opacity = highlighted_opacity
        self.selected_opacity = selected_opacity
        self._shapes = {}

    @property
    def x(self):
        return self.position[0]


    @x.setter
    def x(self, value):
        self.position[0] = value
        self.update_position()


    @property
    def y(self):
        return self.position[1]


    @y.setter
    def y(self, value):
        self.position[1] = value
        self.update_position()

    # @property
    # def position(self):
    #     return self.position


    # @position.setter
    # def position(self, value):
    #     """must by a two-tuple"""
    #     self.position = value


    def is_inside(self, position : pyglet.math.Vec2 = pyglet.math.Vec2() ) -> bool:
        raise NotImplementedError()


    def draw(self) -> None:
        # if self.batch:
        #     self.batch.draw()
        if self.debug:
            self.draw_debug()



    def draw_debug(self) -> None:
        """immediate draw stuff if self.debug = True"""
        raise NotImplementedError()


    def on_mouse_press( self, x, y, buttons, modifiers ):
        # if self.hilighted and buttons & pyglet.window.mouse.LEFT:
        if self.hilighted:
            #print("buttons: %s"%buttons)
            self.dispatch_event("pressed", x, y, buttons, modifiers)
            if buttons & pyglet.window.mouse.LEFT:
                self.selected = True
                self._shapes["select"].opacity = 220 * int(self.selected_opacity)
        else:
            self.selected = False
            self._shapes["select"].opacity = 0 * int(self.selected_opacity)


    def on_mouse_release( self, x, y, buttons, modifiers ):
        if self.hilighted and buttons & pyglet.window.mouse.LEFT:
            self.dispatch_event("released")
            self.selected = False
            self._shapes["select"].opacity = 0 * int(self.selected_opacity)
        else:
            self.selected = False
            self._shapes["select"].opacity = 0 * int(self.selected_opacity)


    def on_mouse_drag( self, x, y, dx, dy, buttons, modifiers):
        if self.selected:
            self.dispatch_event( "dragged" )
            # TODO: camera info!! be class method for converting spaces
            # OR ask mouse for world-space conversion (mouse holds a camera transform)
            if self.mouse:
                if self.space == Handle.SPACE_WORLD:
                    self.position += pyglet.math.Vec2(dx, dy)*(1.0/self.mouse.camera_zoom)
                else:
                    self.position += pyglet.math.Vec2(dx, dy)
            else:
                self.position += pyglet.math.Vec2(dx, dy)
            self.update_position()


    def on_mouse_motion( self, x, y, dx, dy):
        # TODO: fix this, always checks if mouse on every callback
        # ... and only checking here for the test cases that don't set up a boxer mouse
        # ... and is pretty darn WET.
        _prev_mouse_inside = self.mouse_inside
        if self.mouse:
            if not self.mouse.captured_by_ui:
                if self.space == Handle.SPACE_WORLD:
                    mp = self.mouse.world_position
                else:
                    mp = self.mouse.position
                if self.is_inside( pyglet.math.Vec2( mp.x, mp.y ) ):
                    self.hilighted = True
                    self.mouse_inside = True
                    if _prev_mouse_inside is not True:
                        self.dispatch_event("mouse_entered")
                else:
                    self.hilighted = False
                    self.mouse_inside = False
                    if _prev_mouse_inside is True:
                        self.dispatch_event("mouse_exited")
        else:
            if self.is_inside( pyglet.math.Vec2( x, y ) ):
                self.hilighted = True
                self.mouse_inside = True
                if _prev_mouse_inside is not True:
                    self.dispatch_event("mouse_entered")

            else:
                self.hilighted = False
                self.mouse_inside = False
                if _prev_mouse_inside is True:
                    self.dispatch_event("mouse_exited")


        if self.hilighted:
            self._shapes["highlight"].opacity = int(120 * self.highlighted_opacity)
        else:
            self._shapes["highlight"].opacity = int(10 * self.highlighted_opacity)


    def update_position( self, dispatch_event = True, update_all_shapes_positions = True ) -> None:
        if dispatch_event == True:
            ret = self.dispatch_event( "position_updated", self.position )
        if update_all_shapes_positions:
            for k, v in self._shapes.items():
                v.x = self.position.x
                v.y = self.position.y


# ------------------------------------------------------------------------------
# events
Handle.register_event_type("mouse_entered")
Handle.register_event_type("mouse_exited")
Handle.register_event_type("position_updated")
Handle.register_event_type("dragged")
Handle.register_event_type("pressed") # for mouse presses
Handle.register_event_type("released")

# ------------------------------------------------------------------------------

class BoxHandle( Handle):
    def __init__( self,
        name : str = "BoxHandle",
        position : pyglet.math.Vec2 = pyglet.math.Vec2(0.0, 0.0),
        hit_width : float = 75.0,
        display_width : float = 50.0,
        hit_height : float = 45.0,
        display_height : float = 20.0,
        mouse : boxer.mouse.Mouse = None,
        debug : bool = False,
        space : int = Handle.SPACE_WORLD,
        color = (255, 255, 90, 255),
        color_hover = (255, 255, 255, 255),
        batch : pyglet.graphics.Batch = None,
        group : pyglet.graphics.Group = None,
        base_opacity : float = 1.0,
        highlighted_opacity : float = 1.0,
        highlighted_color = (255, 255, 255),
        selected_opacity : float = 1.0,
        selected_color = (255, 0, 0),
        **kwargs
    ):
        Handle.__init__(self,
            name = name,
            position = position,
            mouse = mouse,
            debug = debug,
            space = space,
            batch = batch,
            group = group,
            base_opacity = base_opacity,
            highlighted_opacity = highlighted_opacity,
            selected_opacity = selected_opacity,
            **kwargs
            )

        self._highlighted_color = highlighted_color
        self._selected_color = selected_color

        self._hit_width = hit_width
        self._hit_height = hit_height
        self._display_width = display_width
        self._display_height = display_height

        # _shapes dict
        self._shapes = {}
        # self._shapes["display"] = pyglet.shapes.Rectangle( self.position.x, self.position.y, self._display_width, self._display_height, color=DEBUG_SHAPE_COLOR, batch=self.batch)
        # self._shapes["hit"] = pyglet.shapes.Rectangle( self.position.x, self.position.y, self._hit_width, self._hit_height, color=DEBUG_HIT_SHAPE_COLOR, batch=self.batch)
        # self._shapes["highlight"] = boxer.shapes.RectangleLine(  self.position.x, self.position.y, self._hit_width+2, self._hit_height+2, line_width = 1, color = self._highlighted_color, batch=self.batch)
        # self._shapes["highlight"].opacity = 20
        # self._shapes["select"] = boxer.shapes.RectangleLine(  self.position.x, self.position.y, self._hit_width+4, self._hit_height+4, line_width = 1, color = self._selected_color, batch=self.batch)
        # self._shapes["select"].opacity = 20
        self._shapes["display"] = pyglet.shapes.Rectangle( self.position.x, self.position.y, self._display_width, self._display_height, color=DEBUG_SHAPE_COLOR, batch=self.batch)
        self._shapes["hit"] = pyglet.shapes.Rectangle( self.position.x, self.position.y, self._hit_width, self._hit_height, color=DEBUG_HIT_SHAPE_COLOR, batch=self.batch)
        self._shapes["highlight"] = boxer.shapes.RectangleLine(  self.position.x, self.position.y, self._hit_width+2, self._hit_height+2, line_width = 1, color = self._highlighted_color, batch=self.batch)
        self._shapes["highlight"].opacity = 20
        self._shapes["select"] = boxer.shapes.RectangleLine(  self.position.x, self.position.y, self._hit_width+4, self._hit_height+4, line_width = 1, color = self._selected_color, batch=self.batch)
        self._shapes["select"].opacity = 20

        self.set_shape_anchors()



    @property
    def hit_width(self):
        return self._hit_width


    @hit_width.setter
    def hit_width(self, value):
        self._hit_width = value
        self._shapes["hit"].width = value
        self._shapes["highlight"].width = value +2
        self._shapes["select"].width = value + 4
 

    @property
    def hit_height(self):
        return self._hit_height
 

    @hit_height.setter
    def hit_height(self, value):
        self._hit_height = value
        self._shapes["hit"].height = value
        self._shapes["highlight"].height = value +2
        self._shapes["select"].height = value + 4


    @property
    def display_width(self):
        return self._display_width

    
    @display_width.setter
    def display_width(self, value):
        self._display_width = value
        self._shapes["display"].width = value


    @property
    def display_height(self):
        return self._display_height


    @display_height.setter
    def display_height(self, value):
        self._display_height = value
        self._shapes["display"].height = value




    def is_inside(self, position : pyglet.math.Vec2 = pyglet.math.Vec2()) -> bool:
        """point inside test"""
        # using pyglet.shapes 'in' overloading
        return (position.x, position.y) in self._shapes["hit"]


    def set_shape_anchors(self) -> tuple:
        """sets the anchor position at the centres of self.*_width and self.*_height"""
        self._shapes["display"].anchor_position = (self._display_width / 2.0, self._display_height/2.0)
        self._shapes["hit"].anchor_position = (self._hit_width / 2.0, self._hit_height/2.0)
        self._shapes["highlight"].anchor_position = ( self._shapes["highlight"]._width/2.0, self._shapes["highlight"]._height/2.0 )
        self._shapes["select"].anchor_position = ( self._shapes["select"]._width/2.0, self._shapes["select"]._height/2.0 )
        # self._shapes["temp"].anchor_position = ( self._shapes["temp"]._width/2.0, self._shapes["temp"]._height/2.0 )


class PointHandle( Handle ):
    def __init__(self,
        name : str = "PointHandle",
        position : pyglet.math.Vec2 = pyglet.math.Vec2(),
        mouse : boxer.mouse.Mouse = None,
        debug : bool = False,
        space : int = Handle.SPACE_WORLD,
        hit_radius : float = 15.0,
        display_radius : float = 5.0,
        color = (255, 255, 90, 255),
        color_hover = (255, 255, 255, 255),
        batch : pyglet.graphics.Batch = None,
        group : pyglet.graphics.Group = None,
        base_opacity : float = 1.0,
        highlighted_opacity : float = 1.0,
        selected_opacity : float = 1.0,
        **kwargs
        ):
        
        Handle.__init__(self,
            name = name,
            position = position,
            mouse = mouse,
            debug = debug,
            space = space,
            batch = batch,
            group = group,
            base_opacity = base_opacity,
            highlighted_opacity = highlighted_opacity,
            selected_opacity = selected_opacity,
            **kwargs
            )
        
        self.hit_radius : float = hit_radius
        self.display_radius : float = display_radius

        # dictionary?
        self._shapes = {}
        self._shapes["display"] = pyglet.shapes.Circle( self.position.x, self.position.y, radius=self.display_radius, segments=24, color=DEBUG_SHAPE_COLOR, batch=self.batch)
        self._shapes["hit"] = pyglet.shapes.Circle( self.position.x, self.position.y, radius=self.hit_radius, segments=24, color=DEBUG_HIT_SHAPE_COLOR, batch=self.batch)
        self._shapes["highlight"] = boxer.shapes.Arc( self.position.x, self.position.y, radius=self.hit_radius+1, segments=24, color=(255,255,255), batch=self.batch )
        self._shapes["highlight"].opacity = 20
        self._shapes["select"] = boxer.shapes.Arc( self.position.x, self.position.y, radius=self.hit_radius+3, segments=24, color=(255,70,70), batch=self.batch )
        self._shapes["select"].opacity = 20


    def draw_debug(self):
        # print("PointHandle draw_debug()")
        # pyglet.shapes.Circle( self.position.x, self.position.y, radius=self.hit_radius, color=DEBUG_HIT_SHAPE_COLOR).draw()
        # pyglet.shapes.Circle( self.position.x, self.position.y, radius=self.display_radius, color=DEBUG_SHAPE_COLOR).draw()
        ...
  

    def is_inside( self, position : pyglet.math.Vec2 = pyglet.math.Vec2() ) -> bool:
        """point inside test"""
        # using pyglet.shapes 'in' overloading
        #return  position.distance( self.position ) < self.hit_radius
        return  position in self._shapes["hit"]


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    """handles sandbox"""
    print("run handles.py main:")
    
    sys.path.extend("..")
    import pyglet.window
    from pyglet import app
    from pyglet.window import key
    import math

    _window_config = gl.Config(
        sample_buffers = 1,
        buffer_size = 32,
        samples = 16,
        depth_size = 16,
        double_buffer = True,
    )

    win = pyglet.window.Window(\
                        width=960,
                        height=540,
                        resizable=True,
                        config=_window_config,
                        )
    
    pyglet.gl.glClearColor(0.1, 0.1, 0.1, 1)
    # pyglet.gl.glPolygonMode( pyglet.gl.GL_FRONT_AND_BACK, pyglet.gl.GL_LINE )

    fps_display = pyglet.window.FPSDisplay(win)
    fps_display.update_period = 0.2

    handle_batch = pyglet.graphics.Batch()

    win.global_time = 0.0
    win.delta_time = 0.0

    bh = BoxHandle( name = "BoxHandle_tester",
        position = (win.size[0] /2.0, win.size[1] - 100.0),
        hit_width = 96,
        hit_height = 26,
        display_width = 96 -20,
        display_height = 6,
        batch=handle_batch,
        )

    win.push_handlers( on_mouse_motion = bh.on_mouse_motion )
    win.push_handlers( on_mouse_press = bh.on_mouse_press )
    win.push_handlers( on_mouse_release = bh.on_mouse_release )
    win.push_handlers( on_mouse_drag = bh.on_mouse_drag )


    bh_square = BoxHandle( name = "BoxHandle_square_tester",
        position = (win.size[0] /2.0, win.size[1] - 400.0),
        hit_width = 20,
        hit_height = 20,
        display_width = 10,
        display_height = 10,
        batch=handle_batch,
        )

    win.push_handlers( on_mouse_motion = bh_square.on_mouse_motion )
    win.push_handlers( on_mouse_press = bh_square.on_mouse_press )
    win.push_handlers( on_mouse_release = bh_square.on_mouse_release )
    win.push_handlers( on_mouse_drag = bh_square.on_mouse_drag )


    bh_square2 = BoxHandle( name = "BoxHandle_square_tester",
        position = (win.size[0] /2.0, win.size[1] - 300.0),
        hit_width = 20,
        hit_height = 20,
        display_width = 10,
        display_height = 10,
        batch=handle_batch,
        selected_opacity=1.0,
        highlighted_opacity=0.2
        )

    win.push_handlers( on_mouse_motion = bh_square2.on_mouse_motion )
    win.push_handlers( on_mouse_press = bh_square2.on_mouse_press )
    win.push_handlers( on_mouse_release = bh_square2.on_mouse_release )
    win.push_handlers( on_mouse_drag = bh_square2.on_mouse_drag )


    ph = PointHandle( name = "PointHandle_tester",
        position = (50.0, 50.0),
        debug = True,
        batch=handle_batch
        )

    win.push_handlers( on_mouse_motion = ph.on_mouse_motion )
    win.push_handlers( on_mouse_press = ph.on_mouse_press )
    win.push_handlers( on_mouse_release = ph.on_mouse_release )
    win.push_handlers( on_mouse_drag = ph.on_mouse_drag )


    @win.event
    def on_resize( width, height ):
        """resize"""
        print("main.on_resize (%s, %s)"%(width, height))

    
    
    def on_update(dt):
        win.global_time += dt
        win.delta_time = dt
    
    win.on_update = on_update


    @win.event
    def on_key_press(symbol, _modifiers):
        """key events"""
        if symbol == key.B:
            #####################################
            # make sure there is a breakpoint added
            # on the next 'print' line.
            #####################################
            print("break")


    @win.event
    def on_draw():
        win.clear( )
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)


        s1 = boxer.shaping.remap(math.sin( win.global_time * 8.0 ), -1.0, 1.0, 0.0, 1.0 )
        s1 = boxer.shaping.bias(s1, 0.15)
        s1 = boxer.shaping.remap( s1, 0.0, 1.0, 20.0, 40.0 )

        s2 = boxer.shaping.remap(math.sin( (win.global_time - 0.24)  * 8.0 ), -1.0, 1.0, 0.0, 1.0 )
        s2 = boxer.shaping.bias(s2, 0.15)
        s2 = boxer.shaping.remap( s2, 0.0, 1.0, 20.0, 50.0 )

        s3 = max(s1, s2)

        bh_square.display_width = s3
        bh_square.display_height = s3
        bh_square.hit_width = s3 + 20
        bh_square.hit_height = s3 + 20
        bh_square.set_shape_anchors()

        handle_batch.draw()

        fps_display.draw()
    
    
    pyglet.clock.schedule_interval(win.on_update, 1 / 60.0 )
    app.run()        