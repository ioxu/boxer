import pyglet


# Application
import boxer.application


def test_boxer_application():
    app = boxer.application.Application()
    assert  type(app).__name__ == "Application"


# Background
import boxer.background


def test_boxer_background():
    background = boxer.background.Background()
    assert type(background).__name__ == "Background"