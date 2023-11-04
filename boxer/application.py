import boxer.background
import boxer.mouse
import boxer.camera

import pyglet
import pyglet.gl as gl


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
        self.window = _create_window(res_x, res_y)
        self.on_draw = self.window.event(self.on_draw)
        self.fps_display = pyglet.window.FPSDisplay(self.window)
        self.fps_display.update_period = 0.2

        # app components:
        self.background = boxer.background.Background()
        
        self.mouse = boxer.mouse.Mouse()
        self.window.push_handlers( self.mouse )
        self.window.set_mouse_cursor(self.mouse)

        self.camera = boxer.camera.Camera( self.window )


    def message(self, message):
        """display a message"""
        print("Application(%s).message: %s"%message)


    def on_draw(self):
        self.window.clear()
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        #----------------------
        self.camera.push()
        #----------------------
        self.background.draw()
        #----------------------
        self.camera.pop()
        #----------------------
        gl.glDisable(gl.GL_BLEND)
        self.fps_display.draw()


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