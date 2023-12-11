"""example boxer setup"""

import pyglet
import boxer.application

def main():
    """example boxer program"""
    print("init main()")

    app = boxer.application.Application(name = "boxer")

    pyglet.app.run()

    # app.imgui_renderer.shutdown()

if __name__ == "__main__":
	main()
