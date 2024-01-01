"""boxer.Container tests"""
import pyglet.math
from boxer import handles

def test_Handle_position_getset_x() -> None:
    h = handles.Handle( )
    h.x = 200.0
    assert h.x == 200.0


def test_Handle_position_getset_y() -> None:
    h = handles.Handle( )
    h.y = 300.0
    assert h.y == 300.0


def test_Handle_position_index() -> None:
    h = handles.Handle(position = (6.0, -5.0) )
    assert h.position == (6.0, -5.0)


def test_Handle_position_index_0() -> None:
    h = handles.Handle(position = (3.0, -4.0) )
    assert h.position[0] == 3.0


def test_Handle_position_getset_position() -> None:
    h = handles.Handle(position = (3.0, -4.0) )
    h.position = (-16.0, 17.0)
    assert h.position == (-16.0, 17.0)


def test_Handle_dispatch_event_on_position_uppdated() -> None:
    """testing handle event dispatch"""
    # also, neat to seehow to hook up a handler so simply
    # aslo, very neat to be able to test it

    h = handles.Handle()
    output = [0.0]
    def handler(position):
        output[0] = position.x
    h.push_handlers(on_position_updated = handler)
    h.x = 66.6
    assert output[0] == 66.6

