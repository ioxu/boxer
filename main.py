#! python
"""example boxer setup"""

import pyglet
import boxer.application

def main():
    """example boxer program"""
    print("init main()")

    print("system information:")
    display = pyglet.canvas.get_display()
    print("  display: name: %s - %s"%(display.name, display))
    print("    default_screen: %s"%display.get_default_screen())
    screens = display.get_screens()
    print("    screens:")
    for screen in screens:
        print("      %s"%screen)
        this_mode = screen.get_mode()
        print("      current mode: %s"%this_mode)
        # modes = screen.get_modes()
        # for mode in modes:
        #     print(" "*8 + "%s"%mode)

    app = boxer.application.Application(name = "boxer")

    pyglet.app.run()

    # app.imgui_renderer.shutdown()

if __name__ == "__main__":
	main()
