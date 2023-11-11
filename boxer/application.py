import boxer.background
import boxer.mouse
import boxer.camera

import pyglet
import pyglet.gl as gl
from pyglet.window import key

import imgui
from imgui.integrations.pyglet import create_renderer


class Application(object):
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

        # imgui tests

        self._imgui_io.config_flags += imgui.CONFIG_NO_MOUSE_CURSOR_CHANGE

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
        imgui.begin("Your first window!", True)
        imgui.text("Hello world!")
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
        # TODO: change all this to control my cursors _completely_
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


        #print("want mouse: %s"%self._imgui_io.want_capture_mouse)
        #print("io.config_flags %s"%self._imgui_io.config_flags)
        #print("NO_MOUSE_CURSOR_CHANGE %s" % imgui.CONFIG_NO_MOUSE_CURSOR_CHANGE)
        #print("mouse cursor ID: %s"%imgui.get_mouse_cursor())



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