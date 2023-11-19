# imgui drawing things

import inspect
import imgui

def object_tooltip_info(thing) -> None:
    """returns a bunch of imgui commands to draw text info for an Any obejct"""
    for i in inspect.getmembers( thing ):
        if not i[0].startswith("__"):
            imgui.text( str(i) )
            imgui.same_line()
            imgui.push_style_color( imgui.COLOR_TEXT, 0.5, 0.5, 0.5 )
            imgui.text(str(type(i[1])))
            imgui.pop_style_color(1)
