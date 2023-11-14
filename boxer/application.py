import boxer.background
import boxer.mouse
import boxer.camera

import pyglet
import pyglet.gl as gl
from pyglet.window import key

import imgui
from imgui.integrations.pyglet import create_renderer


class Application(pyglet.event.EventDispatcher):
    """"root application object"""

    application_meta = {}

    def __init__(self,
            name = "default application name",
            res_x = 900,
            res_y = 600):
        
        self.name = name
        print("starting %s"%self)

        # create window before anything else
        self.window : pyglet.window.Window = _create_window(res_x, res_y)
        self.on_draw = self.window.event(self.on_draw)
        self.on_key_press = self.window.event(self.on_key_press)
        self.on_mouse_motion = self.window.event(self.on_mouse_motion)
        self.fps_display = pyglet.window.FPSDisplay(self.window)
        self.fps_display.update_period = 0.2

        # app components:
        self.background = boxer.background.Background()
        
        self.mouse = boxer.mouse.Mouse()
        self.window.push_handlers( self.mouse )
        self.window.set_mouse_cursor(self.mouse)
        #self.system_mouse_cursor = pyglet.window.DefaultMouseCursor()

        self.camera = boxer.camera.Camera( self.window )
        self.window.push_handlers( self.camera )

        # imgui
        imgui.create_context()
        self._imgui_io = imgui.get_io()
        self.imgui_renderer = create_renderer(self.window)
        self._imgui_io.config_flags += imgui.CONFIG_NO_MOUSE_CURSOR_CHANGE # stop imgui ffrom controlling mouse cursor

        # imgui tests
        self._checkbox1_enabled = False
        self.test_vec3_var = pyglet.math.Vec3()
        self.test_vec3_var2 = pyglet.math.Vec3()
        self.push_handlers(on_parameter_changed=self.on_parameter_change)


    def message(self, message):
        """display a message"""
        print("Application(%s).message: %s"%message)


    def on_draw(self):
        self.window.clear()
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        
        #----------------------
        # camera
        self.camera.push()
        #----------------------
        self.background.draw()



    
        #----------------------
        self.camera.pop()
        
        #----------------------
        # screen
        gl.glDisable(gl.GL_BLEND)
        self.fps_display.draw()

        #----------------------
        # gui


        imgui.new_frame()
        imgui.set_next_window_size(210-5, self.window.height-10)
        imgui.set_next_window_position(self.window.width-210, 5)
        imgui.begin("PARAMETERS", closable=False,
                    #flags= imgui.WINDOW_NO_NAV
                    #imgui.WINDOW_NO_TITLE_BAR
                    #imgui.WINDOW_NO_DECORATION
                    )
        
        # imgui.text("PARAMETERS")
        # _, self._checkbox1_enabled = imgui.checkbox("checkbox1", self._checkbox1_enabled)
        # if self._checkbox1_enabled:
        #     imgui.text("    - show stuff because checkbox")

        imgui.push_style_color( imgui.COLOR_HEADER, 0.65, 0.25, 0.025 )
        imgui.push_style_color( imgui.COLOR_HEADER_HOVERED, 0.85, 0.32, 0.05 )
        imgui.push_style_color( imgui.COLOR_HEADER_ACTIVE, 0.95, 0.365, 0.07 )
        expanded1, visible1 = imgui.collapsing_header("info")
        imgui.pop_style_color(3)
        
        if expanded1:
            #imgui.begin_child( "debug", height=60, border=True )
            imgui.push_style_color( imgui.COLOR_TEXT, 0.5, 0.5, 0.5 )
            
            imgui.text("mouse")
            if imgui.is_item_hovered():
                imgui.begin_tooltip()
                imgui.text_unformatted("mouse info goes here, position, state etc...")
                imgui.end_tooltip()
            imgui.text("x:%s y:%s"%(str(self.mouse.position.x), str(self.mouse.position.y)))
            imgui.separator()
            imgui.text("camera")
            cam_pos = self.camera.position
            imgui.text("x:%0.2f y:%0.2f"%( cam_pos[0], cam_pos[1] ))
            imgui.text("zoom:%0.2f"%self.camera.zoom)
            #imgui.end_child()

            imgui.pop_style_color(1)

        #imgui.separator()

        expanded2, visible2 = imgui.collapsing_header("selection")
        
        #imgui.push_style_color(imgui.COLOR_BORDER, 0.2, 0.95, 0.3 )
        imgui.push_style_var(imgui.STYLE_CHILD_BORDERSIZE, 2.0)
        imgui.push_style_var(imgui.STYLE_CHILD_ROUNDING, 5.0)

        if expanded2:
            #imgui.begin_child( "debug two", height=60, border=True )

            imgui.begin_child( "debug two", height=81 , border=True )
            
            imgui.text("name:")
            imgui.same_line()
            imgui.input_text("", "node_1")
            test_vec3_var_changed, self.test_vec3_var = imgui.drag_float3("", *self.test_vec3_var, change_speed=0.001 )
            if test_vec3_var_changed:
                self.dispatch_event("on_parameter_changed", ["test_vec3_var_changed", self.test_vec3_var])
            _, self.test_vec3_var2 = imgui.drag_float3("", *self.test_vec3_var2, change_speed=0.001 )
            imgui.end_child()


        #imgui.pop_style_color(1)
        imgui.pop_style_var(2)
        imgui.end()



        # widgets:
        imgui.show_demo_window()

        imgui.render()
        imgui.end_frame()
        
        self.imgui_renderer.render(imgui.get_draw_data())
        #----------------------




    def on_key_press( self, symbol, modifiers ):
        if symbol == key.R:
			# reset camera
            print("reset camera")
            self.camera.reset()


    def on_mouse_motion(self, x,y,ds,dy):
        
        # set mouse cursor if ImGui wants to capture the mouse:
        # must use a little bit of imgui logic here because imgui sets its own cursors
        # so we need to convert imgui cursor ID to pyglet system mouse cursor ID.
        # Wasn't able to reliably revert control to imgui to set its own cursor again. 
        # TODO: need more control over custom cursors, anyway.
        if self._imgui_io.want_capture_mouse:
            # if self._imgui_io.config_flags & imgui.CONFIG_NO_MOUSE_CURSOR_CHANGE:
            #     self._imgui_io.config_flags -= imgui.CONFIG_NO_MOUSE_CURSOR_CHANGE            
            _im_mouse_cursor = imgui.get_mouse_cursor()
            _im_mouse_cursors = imgui.integrations.pyglet.PygletMixin.MOUSE_CURSORS
            self.window.set_mouse_cursor( self.window.get_system_mouse_cursor( _im_mouse_cursors.get(_im_mouse_cursor) ) )
        else:
            # if not (self._imgui_io.config_flags & imgui.CONFIG_NO_MOUSE_CURSOR_CHANGE):
            #     self._imgui_io.config_flags += imgui.CONFIG_NO_MOUSE_CURSOR_CHANGE
            self.window.set_mouse_cursor(self.mouse)


    # test event ###############################################################
    def on_parameter_change(self, event_arg):
        print(event_arg)
        #print("%s %s"%[event_arg[0], str(event_arg[1:])])
    ############################################################################


# register events --------------------------------------------------------------
Application.register_event_type("on_parameter_changed")


# ------------------------------------------------------------------------------
def _create_window(res_x, res_y):
    """window creator helper"""
    _window_config = gl.Config(
        sample_buffers = 1,
        samples = 4,
        depth_size = 16,
        double_buffer = True,
    )
    _window = pyglet.window.Window(
            res_x, res_y,
            caption = "boxer",
            config = _window_config,
            resizable = True,
            style = pyglet.window.Window.WINDOW_STYLE_DEFAULT           
        )
    return _window