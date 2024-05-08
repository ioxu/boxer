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
                            name='parent_container',
                            position=pyglet.math.Vec2(123,456),
                            use_explicit_dimensions = True
                            )
    c_child = containers.Container(name = 'child_container',)
    c_parent.add_child( c_child )
    c_parent.update()
    assert c_child.get_position_from_parent() == pyglet.math.Vec2(123,456)


def test_Container_set_child_test_parent_children_length() -> None:
    """test exteding children length if set_child index is greater than len(children)"""
    c_parent = containers.Container()
    c_child = containers.Container()
    c_parent.set_child( c_child, 4 )
    assert len(c_parent.children) == 5


def test_Container_add_child_set_child_test_parent_children() -> None:
    """test add_child and then set_child() with index greater than len(children)"""
    c_parent = containers.Container()
    c_child1 = containers.Container()
    c_parent.add_child(c_child1)
    c_child2 = containers.Container()
    c_parent.set_child( c_child2, 5 )
    print(c_parent.children)
    assert c_parent.children == [ c_child1, None, None, None, None, c_child2 ]


def test_Container_remove_child() -> None:
    """test container.remove_child"""
    c_parent = containers.Container()
    c_child1 = containers.Container()
    c_child2 = containers.Container()
    c_parent.add_child(c_child1)
    c_parent.add_child(c_child2)
    c_parent.remove_child( c_child1 )
    assert c_parent.children == [None, c_child2]


def test_Container_remove_child_return_idx() -> None:
    """test container.remove_child returns the index"""
    c_parent = containers.Container()
    c_child1 = containers.Container()
    c_child2 = containers.Container()
    c_child3 = containers.Container()
    c_parent.add_child(c_child1)
    c_parent.add_child(c_child2)
    c_parent.add_child(c_child3)
    idx = c_parent.remove_child( c_child3 )
    assert idx == 2


def test_Container_remove_children() -> None:
    """test for Container.remove_children() """
    c_parent = containers.Container()
    c_child1 = containers.Container()
    c_child2 = containers.Container()
    c_child3 = containers.Container()
    c_parent.add_child(c_child1)
    c_parent.add_child(c_child2)
    c_parent.add_child(c_child3)
    assert c_parent.child_count == 3
    c_parent.remove_children()
    assert c_parent.child_count == 0


def test_Container_remove_children_return_list() -> None:
    """test for Container.remove_children() returning a list"""
    c_parent = containers.Container()
    c_child1 = containers.Container()
    c_child2 = containers.Container()
    c_child3 = containers.Container()
    c_parent.add_child(c_child1)
    c_parent.add_child(c_child2)
    c_parent.add_child(c_child3)
    ex_child_list = c_parent.remove_children()
    print("ex_child_list: %s"%ex_child_list)
    assert ex_child_list == [c_child1, c_child2, c_child3]


def test_Container_remove_children_recursive() -> None:
    """test that a .remove_children will remove the childrens children etc
    (test the recursiveness)"""
    c_parent = containers.Container("parent")
    c_child1 = containers.Container("child1")
    c_parent.add_child(c_child1)
    c_child2 = containers.Container("child2")
    c_child1.add_child(c_child2)
    c_child3 = containers.Container("child3")
    c_child2.add_child(c_child3)
    c_child4 = containers.Container("child4")
    c_child3.add_child(c_child4)
    removed_children = c_parent.remove_children()
    print("removed children: %s"%removed_children)
    assert removed_children == [c_child1, c_child2, c_child3, c_child4]


def test_Container_replace_child() -> None:
    """test container.replace_child equals the replaced child"""
    c_parent = containers.Container()
    c_child1 = containers.Container()
    c_child2 = containers.Container()
    c_parent.add_child(c_child1)
    idx = c_parent.replace_child( c_child1, c_child2 )
    assert c_parent.children[0] == c_child2
    assert idx == 0


def test_Container_replace_by_with_parent() -> None:
    """ test Container.replace equals replaced self"""
    c_parent = containers.Container()
    original_child = containers.Container()
    c_parent.set_child( original_child, index = 0 )
    assert c_parent.children[0] == original_child
    new_instance = containers.Container(name="new container")
    # c_child2 = containers.Container()
    original_child.replace_by( new_instance )
    assert c_parent.children[0] == new_instance


def test_Container_replace_by_without_parent() -> None:
    """test Container.replace equals replaced self"""
    old_container = containers.Container(name="old_container")
    new_container = containers.Container(name="new_container")
    c_replaced = old_container.replace_by( new_container )
    assert c_replaced == new_container


def test_Container_get_root_container() -> None:
    """ """
    c_parent = containers.Container(name="root")
    c_child1 = containers.Container(name="one")
    c_parent.add_child(c_child1)
    c_child2 = containers.Container(name="two")
    c_child1.add_child(c_child2)
    c_child3 = containers.Container(name="three")
    c_child2.add_child(c_child3)
    assert c_child3.get_root_container() == c_parent


# ------------------------------------------------------------------------------
# container actions

def test_Container_action_close_with_no_parent() -> None :
    """test that closing a root container (container with no parent)
    raises a RuntimeWarning"""
    import pytest
    c_parent = containers.Container(name="root")
    with pytest.raises(RuntimeWarning, match='closing a root container is not allowed yet'):
        containers.change_container( c_parent, containers.Container.ACTION_CLOSE )


def test_Container_action_close() -> None:
    # test removing a grandchild
    c_parent = containers.Container(name="root")
    c_child1 = containers.HSplitContainer( name="hsplit", create_default_children=True )
    c_parent.add_child( c_child1 )
    containers.change_container(c_parent.children[0].children[1], containers.Container.ACTION_CLOSE)
    assert c_parent.child_count == 1
    assert isinstance(c_parent.children[0], containers.Container)


# ------------------------------------------------------------------------------
# SplitContainer
def test_SplitContainer_create_default_children() -> None:
    """test SplitContainers creating two default children on
    `create_default_children = True`"""
    c_parent = containers.SplitContainer(name="root", create_default_children=True)
    assert c_parent.child_count == 2 
    assert c_parent.children[0].name == "root_cone"
    assert c_parent.children[1].name == "root_ctwo"


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


def test_HSplitContainer_create_default_children() -> None:
    """test HSplitContainer creating two default children on
    `create_default_children = True`"""
    c_parent = containers.HSplitContainer(name="root", create_default_children=True)
    assert c_parent.child_count == 2 
    assert c_parent.children[0].name == "root_cleft"
    assert c_parent.children[1].name == "root_cright"


# ------------------------------------------------------------------------------
# VSplitContainer

def test_VSplitContainer_create_default_children() -> None:
    """test VSplitContainer creating two default children on
    `create_default_children = True`"""
    c_parent = containers.VSplitContainer(name="root", create_default_children=True)
    assert c_parent.child_count == 2 
    assert c_parent.children[0].name == "root_cbottom"
    assert c_parent.children[1].name == "root_ctop"
