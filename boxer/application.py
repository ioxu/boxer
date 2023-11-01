import boxer.background

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

        # create window before anythign else
        self.window = _create_window(res_x, res_y)
        self.on_draw = self.window.event(self.on_draw)

        self.background = boxer.background.Background()

        # gl.glEnable(gl.GL_BLEND)
        # gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        # gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glClearColor(0.2, 0.3, 0.3, 1)


    def message(self, message):
        """display a message"""
        print("Application(%s).message: %s"%message)


    def on_draw(self):
        self.window.clear()
        self.background.draw()


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