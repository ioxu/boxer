# ui containers
if __name__ == "__main__":
    import sys
    sys.path.extend("..")

import pyglet
import pyglet.graphics
import boxer.camera

# https://www.reddit.com/r/learnprogramming/comments/214nd9/making_a_gui_from_scratch/
# https://developer.valvesoftware.com/wiki/VGUI_Documentation

class Container( pyglet.event.EventDispatcher ):
    def __init__(self,
            name="container",
            window : pyglet.window.Window = None,
            width : int = 128,
            height : int = 128,
            position : pyglet.math.Vec2 = pyglet.math.Vec2(),
            batch : pyglet.graphics.Batch = None,
            group : pyglet.graphics.Group = None,
            ):

        self.name = name
        self.window = window
        self.width = width
        self.height = height
        self.position : pyglet.math.Vec2 = position
        self.batch = batch
        self.group = group

        self.children = []
        self._depth = 0
        self.parent = None


    def add_child(self, child) -> None:
        if child not in self.children:
            child.parent = self
            child.window = self.window
            self.children.append( child )


    def get_child_size(self, this) -> tuple:
        """calculate the width and height available for a child
        ('this' is normally self!)
        subclasses should override this method for their own caclulations
        """
        return (self.width, self.height)


    def get_available_size_from_parent( self ) -> tuple:
        """ask parent for available size"""
        if hasattr(self.parent, "get_child_size"):
            # print("parent type is Container: %s"%type(self.parent)) 
            ps = self.parent.get_child_size( self )
            self.width = ps[0]
            self.height = ps[1]
            return (self.width, self.height)
        elif self.parent == None:#type(self.parent) == type(pyglet.window.Window):
            # print("parent type is pyglet.window.Window: %s"%self.window) 
            ws = self.window.get_size()
            self.width = ws[0]
            self.height = ws[1]
            return (self.width, self.height)#self.window.get_size()
        else:
            return (None, None)


    def get_child_position(self, this):
        print("method: get_child_position %s"%this)
        return self.position


    def get_position_from_parent( self ) -> tuple:
        if hasattr(self.parent, "get_child_position"):
            # print("get_child_position > ")
            self.position = self.parent.get_child_position( self )
            return self.position
        elif self.parent == None:
            # print("get_child_position NONE parent")
            self.position = (0,0)
            return self.position
        else:
            # print("get_child_position ELSE")
            return (None, None)


    @ property
    def child_count(self):
        return len(self.children)


    def update(self) -> None:
        for c in self.children:
            c.update()


    def pprint_tree(self, depth : int = 0) -> None:
        self._depth = depth
        print("    "*depth, "%s %s"%(depth, str(self)), "'%s'"%self.name, "window: %s"%self.window)
        print("    "*depth, "  > size:", self.get_available_size_from_parent(), "position:", self.get_position_from_parent() )
        for c in self.children:
            c.pprint_tree( depth+1 )


    def draw(self):
        # maybe just draw a coloured outline
        pass


class SplitContainer( Container ):
    """container that mannages a split view of two children"""
    def __init__(self,
            ratio : float = 0.5,
            **kwargs):
        Container.__init__( self, **kwargs )
        self.ratio = ratio


class HSplitContainer( SplitContainer ):
    """container managing split view of two child containers,
    first child added is on left, second child on right
    """
    def __init__(self, **kwargs):
        SplitContainer.__init__( self, **kwargs )


    def get_child_size(self, this) -> tuple:
        if this == self.children[0]:
            return (int(self.width*self.ratio), self.height)
        else:
            return (int(self.width*(1-self.ratio)), self.height)


    def get_child_position(self, this) -> tuple:
        # print("HSplit method: get_child_position %s"%this)
        if this == self.children[0]:
            x = self.position[0]
            y = self.position[1]
            return (x, y)
        else:
            x = self.position[0] + int(self.width*self.ratio) +1
            y = self.position[0]
            return (x, y)



class VSplitContainer( SplitContainer ):
    """container managing split view of two child containers,
    first child added is on top, second child on bottom
    """
    def __init__(self, **kwargs):
        SplitContainer.__init__( self, **kwargs )


    def get_child_size(self, this) -> tuple:
        if this == self.children[0]:
            return (self.width, int(self.height * self.ratio))
        else:
            return (self.width, int(self.height * (1.0 - self.ratio)))


    def get_child_position(self, this) -> tuple:
        # print("VSplit method: get_child_position %s"%this)
        if this == self.children[0]:
            x = self.position[0]
            y = self.position[1]
            return (x, y)
        else:
            x = self.position[0]
            y = self.position[0] + int(self.height*self.ratio) +1
            return (x, y)


class ViewportContainer( Container ):
    """ Container that holds an openGL Viewport """
    def __init__(self,
            name="container",
            width : int = 128,
            height : int = 128,
            position : pyglet.math.Vec2 = pyglet.math.Vec2(),
            window : pyglet.window.Window = None,
            camera : boxer.camera.Camera = None
            ):
        Container.__init__(self,
            name = name,
            width = width,
            height = height,
            position = position,
            window = window
        )

        self.camera : boxer.camera.Camera = camera or None
        
        # camera
        if not self.camera:
            print("if not self.camera %s"%self.window)
            print(type(self.window))
            # self.camera = boxer.camera.get_default_camera( self.window )
            self.camera = boxer.camera.get_default_camera( self.window )


    def begin(self) -> None:
        """start the viewport and push the camera's transform onto the view"""
        gl.glViewport(0,0,self.width, self.height)
        self.camera.push()


    def end(self) -> None:
        self.camera.pop()


    def draw(self) -> None:
        # draw the viewport box
        # draw viewport ornaments
        # draw viewport GUI widgets, TODO: Viewport Widgets
        pass


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    print("run containers.py main:")
    
    import sys
    import pyglet.window
    sys.path.extend("..")
    import boxer.camera
    from pyglet import app

    win = pyglet.window.Window( width=960, height=540 )

    # container tree
    c = HSplitContainer(name="root_container", ratio=0.425, window = win)
    c_l = Container(name = "left_panel")
    c_r = VSplitContainer( name = "right panel", ratio =0.33 )
    c.add_child( c_l )
    c.add_child( c_r )

    c_tr = HSplitContainer(name="top_right_panel", ratio=0.33)
    c_tr_1 = Container(name="topright_h1_panel")
    c_tr_2 = Container(name="topright_h2_panel")
    c_tr.add_child(c_tr_1)
    c_tr.add_child(c_tr_2)

    c_vp = ViewportContainer(name="viewport_panel")
    c_r.add_child( c_tr )
    c_r.add_child( c_vp )

    c.pprint_tree()

    app.run()