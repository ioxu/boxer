import boxer.containers as containers


def test_Container_child_count_one() -> None :
    c = containers.Container()
    c.add_child( containers.Container() )
    assert c.child_count == 1


def test_Container_child_count_five() -> None :
    c = containers.Container()
    c.add_child( containers.Container() )
    c.add_child( containers.Container() )
    c.add_child( containers.Container() )
    c.add_child( containers.Container() )
    c.add_child( containers.Container() )
    assert c.child_count == 5


def test_Container_add_HSplitContainer() -> None:
    c = containers.Container()
    c.add_child( containers.HSplitContainer() )
    assert type(c.children[0]) == type( containers.HSplitContainer() )
