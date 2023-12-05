# ui containers
import pyglet

# https://www.reddit.com/r/learnprogramming/comments/214nd9/making_a_gui_from_scratch/
# https://developer.valvesoftware.com/wiki/VGUI_Documentation

class Container( pyglet.event.EventDispatcher ):
    def __init__(self,
            name="container",
            width : int = 128,
            height : int = 128,
            position : pyglet.math.Vec2 = pyglet.math.Vec2()
            ):

        self.name = name
        self.width = width
        self.height = height
        self.position : pyglet.math.Vec2 = position

        self.children = []
        self._depth = 0


    def add_child(self, child) -> None:
        if child not in self.children:
            self.children.append( child )


    @ property
    def child_count(self):
        return len(self.children)


    def update(self) -> None:
        for c in self.children:
            c.update()


    def pprint_tree(self, depth : int = 0) -> None:
        self._depth = depth
        print("    "*depth, "%s %s"%(depth, str(self)), "'%s'"%self.name)
        for c in self.children:
            c.pprint_tree( depth+1 )



class SplitContainer( Container ):
    def __init__(self, **kwargs):
        Container.__init__( self, **kwargs )


class HSplitContainer( SplitContainer ):
    def __init__(self, **kwargs):
        SplitContainer.__init__( self, **kwargs )


class VSplitContainer( SplitContainer ):
    def __init__(self, **kwargs):
        SplitContainer.__init__( self, **kwargs )


class ViewportContainer( Container ):
    def __init__(self,
            name="container",
            width : int = 128,
            height : int = 128,
            position : pyglet.math.Vec2 = pyglet.math.Vec2()
            ):
        Container.__init__(self,
            name=name,
            width = width,
            height = height,
            position = position
        )



# ------------------------------------------------------------------------------
if __name__ == "__main__":
    print("run containers.py main:")

    # tree
    c = Container(name="root_container")
    c1 = Container(name="child_one")
    c.add_child(c1)
    gc2 = Container(name="grandchild_early")
    c1.add_child(gc2)
    ggc1 = Container(name="great_grandchild_one")
    gc2.add_child(ggc1)
    c2 = HSplitContainer(name="child_two")
    c.add_child(c2)
    c2.add_child( Container(name="grandchild_one"))
    c2.add_child( Container(name="grandchild_two"))
    c2.add_child( Container(name="grandchild_three"))
    c2.add_child( ViewportContainer(name="viewport_grandchild"))
    c.pprint_tree()