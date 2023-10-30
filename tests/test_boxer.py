import pyglet
import boxer.application


def test_boxer_application():
    app = boxer.application.Application()
    assert  type(app).__name__ == "Application"

