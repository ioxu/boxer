"""boxer.Container tests"""
import pyglet.math
from boxer import containers


def test_Container_child_count_one() -> None :
    c = containers.Container()
    c.add_child( containers.Container() )
    c.update()
    assert c.child_count == 1


def test_Container_child_count_five() -> None :
    c = containers.Container()
    c.add_child( containers.Container() )
    c.add_child( containers.Container() )
    c.add_child( containers.Container() )
    c.add_child( containers.Container() )
    c.add_child( containers.Container() )
    c.update()
    assert c.child_count == 5


def test_Container_add_HSplitContainer() -> None:
    c = containers.Container()
    c.add_child( containers.HSplitContainer() )
    c.update()
    assert isinstance(c.children[0], containers.HSplitContainer)


def test_Container_use_explicit_dimensions_true() -> None:
    """test combination of get_position_from_parent() and use_explicit_dimensions arg
    EQUAL TO explicit position
    """
    c_parent = containers.Container( name = "parent")
    c_child = containers.Container(\
                            position=pyglet.math.Vec2(123, 456),
                            use_explicit_dimensions=True )
    c_parent.add_child( c_child )
    c_parent.update()
    assert c_child.get_position_from_parent() == pyglet.math.Vec2(123, 456)


def test_Container_use_explicit_dimensions_false() -> None:
    """test combination of get_position_from_parent() and use_explicit_dimensions arg
    NOT EQUAL TO explicit position
    """
    c_parent = containers.Container( name = "parent")
    c_child = containers.Container(\
                            position=pyglet.math.Vec2(123, 456),
                            use_explicit_dimensions=False )
    c_parent.add_child( c_child )
    c_parent.update()
    assert c_child.get_position_from_parent() != pyglet.math.Vec2(123, 456)


def test_Container_get_position_from_parent() -> None:
    """test method .get_position_from_parent"""
    c_parent = containers.Container(\
                            position=pyglet.math.Vec2(123,456))
    c_child = containers.Container()
    c_parent.add_child( c_child )
    c_parent.update()
    # print(c_parent.get_position_from_parent())
    assert c_child.get_position_from_parent() == pyglet.math.Vec2(123,456)


# ------------------------------------------------------------------------------
# HSplitContainer

def test_HSplitContainer_get_position_from_parent() -> None:
    """test the x position returned for the second child of an HSplitContainer"""
    c_parent = containers.HSplitContainer(\
                            ratio = 0.5,
                            width = 100,
                            position=pyglet.math.Vec2(25,0))
    c_child_left = containers.Container()
    c_child_right = containers.Container()
    c_parent.add_child( c_child_left )
    c_parent.add_child( c_child_right )
    print( c_child_left.get_position_from_parent() )
    print( c_child_right.get_position_from_parent() )
    assert c_child_right.get_position_from_parent()[0] == 75



