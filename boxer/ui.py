# imgui drawing things
import pyglet
import imgui
import inspect

#from tkinter import filedialog, Tk
import tkinter.filedialog
import tkinter


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


# main application gui things --------------------------------------------------
def main_menu_bar( application_root ) -> None:
    """main menu bar"""
    with imgui.begin_main_menu_bar() as main_menu_bar:
        if main_menu_bar.opened:
            with imgui.begin_menu("File", True) as file_menu:
                if file_menu.opened:
                    imgui.menu_item('New', 'Ctrl+N', False, True)
                    imgui.menu_item('Open...', 'Ctrl+O', False, True)
                    _save_clicked, _state = imgui.menu_item('Save', 'Ctrl+S', False, True)
                    # ----------------------------------------------------------
                    if _save_clicked:
                        application_root.save_file()
                    # ----------------------------------------------------------

                    _save_as_clicked, _state = imgui.menu_item('Save As...', 'Shift+Ctrl+S', False, True)
                    # ----------------------------------------------------------
                    if _save_as_clicked:
                        file_path = browse_save_file_path()
                        application_root.do_save_as_file( file_path )
                    # ----------------------------------------------------------

                    imgui.separator()
                    imgui.menu_item('Recent Files ..', 'Ctrl+R', False, True)
                    imgui.separator()
                    imgui.menu_item('Settings', None, False, True)
                    imgui.separator()
                    _clicked, _state = imgui.menu_item("Quit", None, False, True)
                    if _clicked:
                        print("Quit via manin menu")
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


# ------------------------------------------------------------------------------
def object_tooltip_info(thing) -> None:
    """returns a bunch of imgui commands to draw text info for an Any object"""
    for i in inspect.getmembers( thing ):
        if not i[0].startswith("__"):
            imgui.text( str(i) )
            imgui.same_line()
            imgui.push_style_color( imgui.COLOR_TEXT, 0.5, 0.5, 0.5 )
            imgui.text(str(type(i[1])))
            imgui.pop_style_color(1)
