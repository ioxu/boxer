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
        # self.on_mouse_scroll = self.window.event(self.on_mouse_scroll)
        # self.on_mouse_drag = self.window.event(self.on_mouse_drag)
        # self.on_mouse_press = self.window.event(self.on_mouse_press)
        # self.on_mouse_release = self.window.event(self.on_mouse_release)

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

        # gui settings
        self.parameter_panel_width = 210
        self.parameter_panel_width_original = self.parameter_panel_width

        # imgui tests
        self._checkbox1_enabled = False
        self.test_vec3_var = pyglet.math.Vec3()
        self.test_vec3_var2 = pyglet.math.Vec3()
        self.push_handlers(on_parameter_changed=self.on_parameter_change)
        self.test_node_name = "node_1"


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

        # menu bar
        with imgui.begin_main_menu_bar() as main_menu_bar:
            if main_menu_bar.opened:
                with imgui.begin_menu("File", True) as file_menu:
                    if file_menu.opened:
                        imgui.menu_item('New', 'Ctrl+N', False, True)
                        imgui.menu_item('Open ...', 'Ctrl+O', False, True)
                        imgui.separator()
                        imgui.menu_item('Recent Files ..', 'Ctrl+R', False, True)
                        imgui.separator()
                        imgui.menu_item('Settings', None, False, True)
                with imgui.begin_menu("Graph", True) as graph_menu:
                    if graph_menu.opened:
                        imgui.menu_item("Add Graph", 'Ctrl+G', False, True)
                        imgui.menu_item("Merge Graph", 'Ctrl+M', False, True)
                        imgui.menu_item("Split Graph", 'Ctrl+P', False, True)
                        imgui.menu_item("Export Graph", 'Ctrl+P', False, True)
                        imgui.separator()
                        imgui.text("open graphs:")
                        imgui.menu_item("graph_01", 'Ctrl+1', False, True)
                        imgui.menu_item("graph_02", 'Ctrl+2', False, True)
                        imgui.menu_item("spread_15", 'Ctrl+3', False, True)

        # parameters pane
        imgui.set_next_window_size(self.parameter_panel_width-5, self.window.height - 10 - 18)
        imgui.set_next_window_position(self.window.width-self.parameter_panel_width, 18 + 5)
        ret=imgui.begin("PARAMETERS", closable=False,
                    #flags= imgui.WINDOW_NO_NAV
                    #imgui.WINDOW_NO_TITLE_BAR
                    #imgui.WINDOW_NO_DECORATION
                    )
        
        # print(ret)
        # print(imgui.get_content_region_available().x)

        # MAGIC NUMBER ---------------------------------------------------------
        self.parameter_panel_width = imgui.get_content_region_available().x + 21
        #-----------------------------------------------------------------------


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
            if self.camera.enabled:
                imgui.text("camera")
            else:
                imgui.text("camera (disabled)")
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


            imgui.push_item_width(-1)
            name_changed, self.test_node_name = imgui.input_text("", self.test_node_name,
                callback=text_input_callback,
                user_data="test_node_name_callback_user_data",
                flags=imgui.INPUT_TEXT_AUTO_SELECT_ALL)
            imgui.pop_item_width()
            
            if name_changed:
                print( "name_changed: %s"%self.test_node_name )


            # imgui.push_item_width(-1)
            # name_changed, self.test_node_name = imgui.input_text("", self.test_node_name,
            #     callback=text_input_callback,
            #     user_data="test_node_name_callback_user_data",
            #     flags=imgui.INPUT_TEXT_AUTO_SELECT_ALL|imgui.INPUT_TEXT_ENTER_RETURNS_TRUE)
            # imgui.pop_item_width()
            
            # if name_changed:
            #     print( "name_changed: %s"%self.test_node_name )


            # imgui.push_item_width(-1)
            # if imgui.input_text("", self.test_node_name,
            #             callback=text_input_callback,
            #             user_data="test_node_name_callback_user_data",
            #             #flags=imgui.INPUT_TEXT_AUTO_SELECT_ALL|imgui.INPUT_TEXT_ENTER_RETURNS_TRUE):
            #             flags=imgui.INPUT_TEXT_ENTER_RETURNS_TRUE):
            #             #):

            #     print("return : %s"%self.test_node_name)

            # imgui.pop_item_width()

            test_vec3_var_changed, self.test_vec3_var = imgui.drag_float3("parm1", *self.test_vec3_var, change_speed=0.001 )
            if test_vec3_var_changed:
                self.dispatch_event("on_parameter_changed", ["test_vec3_var_changed", self.test_vec3_var])
            imgui.push_item_width(-1)
            
            _, self.test_vec3_var2 = imgui.drag_float3("3var", *self.test_vec3_var2, change_speed=0.001 )
            if _:
                print("changed value: %s"%str(self.test_vec3_var2))
            imgui.pop_item_width()
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


# register events --------------------------------------------------------------
Application.register_event_type("on_parameter_changed")


def text_input_callback(value):
    print("callback: %s"%value)
    #print("callback: %s"%str(dir(value)))
    print("    buffer %s"%value.buffer)
    print("    buffer_dirty %s"%value.buffer_dirty)
    print("    buffer_size %s"%value.buffer_size)
    print("    clear_selection %s"%value.clear_selection)
    print("    event_char %s"%value.event_char)
    print("    event_flag %s"%value.event_flag)
    print("    event_key %s"%value.event_key)
    print("    flags %s"%value.flags)
    print("    has_selection() %s"%value.has_selection())
    print("    select_all() %s"%value.select_all())
    print("    selection_end %s"%value.selection_end)
    print("    selection_start %s"%value.selection_start)
    print("    user_data %s"%value.user_data)
    pass

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