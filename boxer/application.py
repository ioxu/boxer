import boxer.background
import boxer.mouse
import boxer.camera
import boxer.ui

import pyglet
import pyglet.gl as gl
from pyglet.window import key

import imgui
# from imgui.integrations.pyglet import create_renderer

from colour import Color
import os, math, types


class Application(pyglet.event.EventDispatcher):
    """"root application object"""

    application_meta = {}

    def __init__(self,
            name = "boxer",
            res_x = 900,
            res_y = 600):
        
        self.name = name
        print("starting %s"%self)

        # create window before anything else
        self.window : pyglet.window.Window = _create_window(res_x, res_y)
        self.window.set_icon(
            # pyglet.image.load("boxer/resources/icon-64.png"),
            # pyglet.image.load("boxer/resources/icon-32.png"),
            # pyglet.image.load("boxer/resources/icon-16.png"))
            pyglet.image.load(os.path.join("boxer","resources", "icon-64.png")),
            pyglet.image.load(os.path.join("boxer","resources", "icon-32.png")),
            pyglet.image.load(os.path.join("boxer","resources", "icon-16.png")))
        self.fullscreen = False


        self.on_close = self.window.event(self.on_close)
        self.on_draw = self.window.event(self.on_draw)
        self.on_key_press = self.window.event(self.on_key_press)
        self.on_mouse_motion = self.window.event(self.on_mouse_motion)
        # self.on_mouse_scroll = self.window.event(self.on_mouse_scroll)
        # self.on_mouse_drag = self.window.event(self.on_mouse_drag)
        # self.on_mouse_press = self.window.event(self.on_mouse_press)
        # self.on_mouse_release = self.window.event(self.on_mouse_release)

        self.fps_display = pyglet.window.FPSDisplay(self.window)
        self.fps_display.update_period = 0.2
        self.fps_display.label.y = 60

        # app components:
        self.background = boxer.background.Background()
        
        self.mouse = boxer.mouse.Mouse()
        self.window.push_handlers( self.mouse )
        self.window.set_mouse_cursor(self.mouse)
        # self.system_mouse_cursor = pyglet.window.DefaultMouseCursor()

        self.camera = boxer.camera.Camera( self.window )
        self.window.push_handlers( self.camera )
        self.camera.push_handlers(transform_changed=self.mouse.on_camera_transform_changed)
        self.camera.start()

        # serialisation
        self.file_path = ""

        # imgui
        self.ui = boxer.ui.Ui( application_root=self )
        self.ui.push_handlers(on_parameter_changed=self.on_parameter_change) # register to Ui events
        
        # imgui.create_context()
        self._imgui_io = imgui.get_io()
        # self.imgui_renderer = create_renderer(self.window)
        # self._imgui_io.config_flags += imgui.CONFIG_NO_MOUSE_CURSOR_CHANGE # stop imgui ffrom controlling mouse cursor

        # gui settings
        # self.parameter_panel_width = 210
        # self.parameter_panel_width_original = self.parameter_panel_width

        # imgui tests
        self._checkbox1_enabled = False
        self.test_vec3_var = pyglet.math.Vec3()
        self.test_vec3_var2 = pyglet.math.Vec3()
        self.test_node_name = "node_1"
        self.test_graph_name = "graph_01"

        self.graph_label = pyglet.text.Label(
            str(self.test_graph_name),
            font_size = 30.0,
            color = (255,255,255, 80),
            x = 10, y = 20
        )

        # self.test_decal = pyglet.resource.image('boxer/resources/test_decal.png')#pyglet.image.load( 'boxer/resources/test_decal.png' )
        # gl.glGenerateMipmap(gl.GL_TEXTURE_2D)
        # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER,
        #         gl.GL_LINEAR_MIPMAP_LINEAR)
        # gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_LOD_BIAS, 0)

        # import sys
        # print("%s %s"%(self, sys.getsizeof(self)))


    def save_file(self,  save_as = False, browse = True ):
        """save the project to a file
        First checks if self.file_path is defined.
        
        `save_as` : bool
            spawn a filebrowser even if self.file_path is defined.
        `browse` : bool
            spawn a filebrowser if necessary, otherwise pass.
        """
        
        if self.file_path != "" and not save_as:
            print("Ctrl-S to %s"%self.file_path)
            self.save_to_file( self.file_path )
        else:
            if browse:
                file_path = boxer.ui.browse_save_file_path()
                self.save_to_file( file_path )
            else:
                pass


    def save_to_file(self, file_path ) -> bool:
        """saves a description of the project to a given filepath
        
        Returns True if saved, Fales if file_path is empty
        """
        
        if file_path == '':
            return False

        import json
        import datetime

        app_dict = {
            "utc-iso-timestamp":datetime.datetime.utcnow().isoformat(),
            "timestamp":str(datetime.datetime.now()).split('.')[0],
            "application": self.as_json(),
            "graph":{
                "name": self.test_graph_name,
                "background": self.background.as_json(),
                "camera": self.camera.as_json()
                }
            }

        json_data = json.dumps( app_dict, indent=4)

        with open(file_path, "w") as outfile:
            saved_bytes = outfile.write(json_data)
        print("save_as_file(%s) done (%s bytes)"%(file_path, str(saved_bytes)))
        self.file_path = file_path
        self.window.set_caption(self.name + "  -  [" + self.file_path+"]")
        return True


    def as_json(self)->dict:
        return{
            "name":self.name,
        }


    def message(self, message):
        """display a message"""
        print("Application(%s).message: %s"%message)


    def on_draw(self):
        self.window.clear()
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)


        gl.glViewport(int(self.window.width/2.0), 0, int(self.window.width/2.0), self.window.height  )
        self.background.draw()

        gl.glViewport(0, 0, int(self.window.width/2.0)-1, self.window.height  )

        #----------------------
        # camera
        self.camera.push()
        #----------------------

        self.background.draw()

        line_width = 3.0 * self.camera.zoom
        gl.glLineWidth(line_width)

        c = (255, 255, 255, 50)
        boxer.shapes.Arc( 0.0, 35.0, 35, segments=128, angle = math.tau*0.25, start_angle=math.tau*-0.25, color = c).draw()
        pyglet.shapes.Line(  35.0, 35.0, 35.0, 135.0, color=c, width=3.0).draw()
        boxer.shapes.Arc( 35.0*2.0, 135.0, 35, segments=128, angle = math.tau*-0.25, start_angle=math.tau*-0.5, color = c).draw()
        boxer.shapes.Arc( -50.0, -50.0, 50, segments=64,  color=c ).draw()  
        pyglet.shapes.BezierCurve((0,0), (0,200), (200,200), (200, 400), segments=32, color=c).draw()
        pyglet.shapes.BezierCurve((0,0), (0,200), (300,200), (300, 400), segments=32, color=c).draw()

        c = (199, 71, 71, 153)
        gl.glLineWidth(30.0* self.camera.zoom)
        pyglet.shapes.BezierCurve((0,0), (0,200), (-400,200), (-400, 400), segments=64, color=c).draw()
        c = (223, 167, 1, 153)
        gl.glLineWidth(10.0* self.camera.zoom)
        pyglet.shapes.BezierCurve((-10,0), (-10,200-10), (-410,200-10), (-410, 400), segments=64, color=c).draw()


        #----------------------
        self.camera.pop()
        #----------------------
        # screen
        
        gl.glViewport(0,0,self.window.width, self.window.height)
        self.fps_display.draw()
        self.graph_label.draw()
        
        # graphic
        # gl.glEnable(gl.GL_BLEND)
        # gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        # decal_scale = 0.2
        # padding = 5
        # self.test_decal.blit( \
        #     self.window.width - (self.test_decal.width * decal_scale) - padding,
        #     padding,
        #     width = self.test_decal.width * decal_scale,
        #     height = self.test_decal.height * decal_scale)
        
        #----------------------
        # ui
        self.ui.draw()
        #----------------------



    def on_key_press( self, symbol, modifiers ):
        if symbol == key.R:
			# reset camera
            print("reset camera")
            self.camera.reset()
        
        if symbol == key.ESCAPE:
            return pyglet.event.EVENT_HANDLED 
        
        # Save: Ctrl-S
        if symbol == key.S: 
            if modifiers & key.MOD_CTRL and modifiers & key.MOD_SHIFT:
                print("Shift-Ctrl-S : Save As")
                self.save_file( save_as = True)
            elif modifiers & key.MOD_CTRL:
                print("Ctrl-S : Save")
                self.save_file()

        # Alt-Enter: toggle fullscreen
        if symbol == key.ENTER:
            if modifiers & key.MOD_ALT:
                self.toggle_fullscreen()


    def toggle_fullscreen(self) -> None:
        self.fullscreen = not self.fullscreen
        self.window.set_fullscreen( self.fullscreen )


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
        
            self.camera.disable()
        else:
            # if not (self._imgui_io.config_flags & imgui.CONFIG_NO_MOUSE_CURSOR_CHANGE):
            #     self._imgui_io.config_flags += imgui.CONFIG_NO_MOUSE_CURSOR_CHANGE
            self.camera.enable()
            self.window.set_mouse_cursor(self.mouse)


    # def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
    #     if self._imgui_io.want_capture_mouse:
    #         return pyglet.event.EVENT_HANDLED


    # def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
    #     if self._imgui_io.want_capture_mouse:
    #         return pyglet.event.EVENT_HANDLED


    # def on_mouse_press(self, x, y, buttons, modifiers):
    #     if self._imgui_io.want_capture_mouse:
    #         return pyglet.event.EVENT_HANDLED


    # def on_mouse_release(self, x, y, buttons, modifiers):
    #     if self._imgui_io.want_capture_mouse:
    #         return pyglet.event.EVENT_HANDLED


    # test event ###############################################################
    def on_parameter_change(self, event_arg):
        print("dispatched event: 'on_parameter_change' %s"%event_arg)
        #print("%s %s"%[event_arg[0], str(event_arg[1:])])
    ############################################################################

    def on_close(self):
        print("%s on_close"%self)
        self.ui.on_close()


# ------------------------------------------------------------------------------
def _create_window(res_x, res_y):
    """window creator helper"""
    _window_config = gl.Config(
        sample_buffers = 1,
        samples = 16,
        depth_size = 16,
        double_buffer = True,
    )
    _window = pyglet.window.Window(
            res_x, res_y,
            caption = "boxer",
            config = _window_config,

            # resizable = False,
            # style = pyglet.window.Window.WINDOW_STYLE_BORDERLESS,
            resizable = True,
            style=pyglet.window.Window.WINDOW_STYLE_DEFAULT

        )
    return _window


# ------------------------------------------------------------------------------
def to_255i(in_tuple : tuple)->tuple:
    return tuple([int(i*255) for i in in_tuple])