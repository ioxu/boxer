# imgui drawing things
import pyglet
import imgui
from imgui.integrations.pyglet import create_renderer
import inspect

#from tkinter import filedialog, Tk
import tkinter.filedialog
import tkinter

# main application gui things --------------------------------------------------
class Ui(pyglet.event.EventDispatcher):
    """main Ui class"""
    def __init__(self,
            application_root = None):
        self.application_root = application_root
        # visibilities ---------------------------------------------------------
        self.main_menu_bar_visible = True
        self.parameter_pane_visible = True
        self.imgui_demo_visible = False
        # parameter pane -------------------------------------------------------
        self.parameter_panel_width = 210
        self.parameter_panel_width_original = self.parameter_panel_width
        # init imgui -----------------------------------------------------------
        imgui.create_context()
        self._imgui_io = imgui.get_io()
        self.imgui_renderer = create_renderer(self.application_root.window)
        # stop imgui from controlling mouse cursor:
        self._imgui_io.config_flags += imgui.CONFIG_NO_MOUSE_CURSOR_CHANGE



    def main_menu_bar(self ) -> None:
        """main menu bar"""
        imgui.push_style_var(imgui.STYLE_FRAME_PADDING, imgui.Vec2(0.0, 10.0))
        with imgui.begin_main_menu_bar() as main_menu_bar:
            imgui.pop_style_var(1)
            if main_menu_bar.opened:
                with imgui.begin_menu("File", True) as file_menu:
                    if file_menu.opened:
                        imgui.menu_item('New', 'Ctrl+N', False, True)
                        imgui.menu_item('Open...', 'Ctrl+O', False, True)
                        # ----------------------------------------------------------
                        _save_clicked, _state = imgui.menu_item('Save', 'Ctrl+S', False, True)
                        # ----------------------------------------------------------
                        if _save_clicked:
                            self.application_root.save_file()
                        # ----------------------------------------------------------
                        _save_as_clicked, _state = imgui.menu_item('Save As...', 'Shift+Ctrl+S', False, True)
                        # ----------------------------------------------------------
                        if _save_as_clicked:
                            file_path = browse_save_file_path()
                            self.application_root.save_to_file( file_path )
                        # ----------------------------------------------------------
                        imgui.separator()
                        imgui.menu_item('Recent Files ..', 'Ctrl+R', False, True)
                        imgui.separator()
                        imgui.menu_item('Settings', None, False, True)
                        imgui.separator()
                        _clicked, _state = imgui.menu_item("Quit", None, False, True)
                        if _clicked:
                            print("Quit via main menu")
                            #self.application_root.on_close()
                            pyglet.app.exit()


                with imgui.begin_menu("Graph", True) as graph_menu:
                    if graph_menu.opened:
                        imgui.menu_item("Add Graph", 'Ctrl+G', False, True)
                        imgui.menu_item("Merge Graph", 'Ctrl+M', False, True)
                        imgui.menu_item("Split Graph", 'Ctrl+P', False, True)
                        imgui.menu_item("Export Graph", 'Ctrl+P', False, True)
                        imgui.separator()
                        imgui.push_style_color( imgui.COLOR_TEXT, 0.5, 0.5, 0.5 )
                        imgui.text("open graphs:")
                        imgui.pop_style_color()
                        imgui.menu_item("graph_01", 'Ctrl+1', False, True)
                        imgui.menu_item("graph_02", 'Ctrl+2', False, True)
                        imgui.menu_item("spread_15", 'Ctrl+3', False, True)


                with imgui.begin_menu("View", True) as view_menu:
                    if view_menu.opened:
                        _parameters_clicked, _parameters_state = imgui.menu_item("Parameters", selected = self.parameter_pane_visible)
                        if _parameters_clicked:
                            self.parameter_pane_visible = not self.parameter_pane_visible
                        imgui.separator()
                        _demo_clicked, _demo_state = imgui.menu_item("Dear ImGui Demo", selected = self.imgui_demo_visible)
                        if _demo_clicked:
                            self.imgui_demo_visible = not self.imgui_demo_visible



                with imgui.begin_menu("Help", True) as help_menu:
                    if help_menu.opened:
                        imgui.menu_item("about boxer")


    def  parameter_pane(self):
        # parameters pane
        imgui.set_next_window_size(self.parameter_panel_width-5, self.application_root.window.height - 10 - 18)
        imgui.set_next_window_position(self.application_root.window.width-self.parameter_panel_width, 18 + 5)
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

        imgui.push_style_color( imgui.COLOR_HEADER, 0.3, 0.3, 0.3 )
        imgui.push_style_color( imgui.COLOR_HEADER_HOVERED, 0.4, 0.4, 0.4 )
        imgui.push_style_color( imgui.COLOR_HEADER_ACTIVE, 0.5, 0.5, 0.5 )
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
            imgui.text("x:%s y:%s"%(str(self.application_root.mouse.position.x), str(self.application_root.mouse.position.y)))
            imgui.separator()
            if self.application_root.camera.enabled:
                imgui.text("camera")
            else:
                imgui.text("camera (disabled)")
            cam_pos = self.application_root.camera.position
            imgui.text("x:%0.2f y:%0.2f"%( cam_pos[0], cam_pos[1] ))
            imgui.text("zoom:%0.2f"%self.application_root.camera.zoom)
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
            name_changed, self.application_root.test_node_name = imgui.input_text("",
                self.application_root.test_node_name,
                callback=text_input_callback,
                user_data="test_node_name_callback_user_data",
                flags=imgui.INPUT_TEXT_AUTO_SELECT_ALL)
            imgui.pop_item_width()
            
            if name_changed:
                print( "name_changed: %s"%self.application_root.test_node_name )


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

            test_vec3_var_changed, self.application_root.test_vec3_var =\
                    imgui.drag_float3("parm1",
                        *self.application_root.test_vec3_var,
                        change_speed=0.001 )
            if test_vec3_var_changed:
                self.dispatch_event("on_parameter_changed", ["test_vec3_var_changed", self.application_root.test_vec3_var])
            imgui.push_item_width(-1)
            
            _, self.application_root.test_vec3_var2 = imgui.drag_float3("3var", *self.application_root.test_vec3_var2, change_speed=0.001 )
            if _:
                print("changed value: %s"%str(self.application_root.test_vec3_var2))
            imgui.pop_item_width()
            imgui.end_child()


        #imgui.pop_style_color(1)
        imgui.pop_style_var(2)
        
        imgui.push_style_color( imgui.COLOR_HEADER, 0.65, 0.25, 0.025 )
        imgui.push_style_color( imgui.COLOR_HEADER_HOVERED, 0.85, 0.32, 0.05 )
        imgui.push_style_color( imgui.COLOR_HEADER_ACTIVE, 0.95, 0.365, 0.07 )
        expanded3, visible3 = imgui.collapsing_header("graph")
        imgui.pop_style_color(3)
        
        imgui.push_style_color( imgui.COLOR_FRAME_BACKGROUND, 0.65*0.6, 0.25*0.6, 0.02*0.6 )
        if expanded3:
            # expanded4, visible4 = imgui.collapsing_header("details", flags = imgui.TREE_NODE_FRAMED)            
            # if expanded4:

            #imgui.push_style_color( imgui.COLOR_TEXT, *Color(rgb=(1, 0, 0)).rgb )
            imgui.text("name:")
            imgui.same_line()
            imgui.push_item_width(-1)
            name_changed, self.application_root.test_graph_name =\
                    imgui.input_text("name_input",
                    self.application_root.test_graph_name,
                    flags=imgui.INPUT_TEXT_AUTO_SELECT_ALL)
            imgui.pop_item_width()
            if name_changed:
                #print(self.test_graph_name)
                self.application_root.graph_label.text = str(self.application_root.test_graph_name)
                
            if imgui.tree_node("background", flags = imgui.TREE_NODE_DEFAULT_OPEN):

                imgui.push_item_width(-1)
                imgui.text("one")
                imgui.same_line()
                #_colour_one_changed, self.background.colour_one = imgui.color_edit3("colour_one", *self.background.colour_one, flags = imgui.COLOR_EDIT_FLOAT)
                _colour_one_changed, _colour_one_value = imgui.color_edit3("colour_one", *self.application_root.background.colour_one, flags = imgui.COLOR_EDIT_FLOAT)
                if _colour_one_changed:
                    self.application_root.background.set_colour_one( _colour_one_value )
                imgui.text("two")
                imgui.same_line()
                #_colour_two_changed, self.background.colour_two = imgui.color_edit3("colour_two", *self.background.colour_two, flags = imgui.COLOR_EDIT_FLOAT)
                _colour_two_changed, _colour_two_value = imgui.color_edit3("colour_two", *self.application_root.background.colour_two, flags = imgui.COLOR_EDIT_FLOAT)
                if _colour_two_changed:
                    self.application_root.background.set_colour_two( _colour_two_value )
                imgui.pop_item_width()

                imgui.text("image:")
                #imgui.same_line()
                imgui.image(self.application_root.background.texture.id,
                    self.application_root.background.texture.width,
                    self.application_root.background.texture.height,
                    border_color=(1, 0, 0, 1))

                imgui.separator()
                imgui.push_style_color( imgui.COLOR_TEXT, 0.5, 0.5, 0.5 )
                imgui.text("object:")
                imgui.pop_style_color(1)
                imgui.text(str(self.application_root.background))
                if imgui.is_item_hovered():
                    with imgui.begin_tooltip():
                        imgui.text('name: "%s"'%str(self.application_root.background.name))
                        imgui.text("object: %s"%str(self.application_root.background))
                        imgui.separator()
                        object_tooltip_info(self.application_root.background)

                imgui.tree_pop()

            #imgui.pop_style_color()
        imgui.pop_style_color(1)
        imgui.end()


    def draw(self):
        imgui.new_frame()

        if self.main_menu_bar_visible:
            self.main_menu_bar()
        if self.parameter_pane_visible:
            self.parameter_pane()
        if self.imgui_demo_visible:
            imgui.show_demo_window()

        imgui.render()
        imgui.end_frame()
        self.imgui_renderer.render(imgui.get_draw_data())


    def on_close(self):
        print("%s on_close"%self)
        print("shutting down imgui renderer")
        self.imgui_renderer.shutdown()


# ------------------------------------------------------------------------------
# Ui events registrar
Ui.register_event_type("on_parameter_changed")


# ------------------------------------------------------------------------------
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
def browse_save_file_path() -> str:
    """open a file dialog to browse a filepath to save to"""
    
    root = tkinter.Tk()
    root.withdraw()  # Hide the main window
    file_path = tkinter.filedialog.asksaveasfilename(
        defaultextension = ".json",
        filetypes = [("JSON", "*.json"),('boxer project files', '*.bxr'), ('All files', '*.*')],
        title = "Save As"
    )
    print("chosen file path: '%s'"%file_path)
    root.destroy()    
    return file_path


def object_tooltip_info(thing) -> None:
    """returns a bunch of imgui commands to draw text info for an Any object"""
    for i in inspect.getmembers( thing ):
        if not i[0].startswith("__"):
            imgui.text( str(i) )
            imgui.same_line()
            imgui.push_style_color( imgui.COLOR_TEXT, 0.5, 0.5, 0.5 )
            imgui.text(str(type(i[1])))
            imgui.pop_style_color(1)
