# ui containers
if __name__ == "__main__":
    import sys
    sys.path.extend("..")

import pyglet
import pyglet.graphics
import pyglet.shapes
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
            color = (255, 255, 255, 60),
            batch : pyglet.graphics.Batch = None,
            group : pyglet.graphics.Group = None,
            ):

        self.name = name
        self.window = window
        self.width = width
        self.height = height
        self.position : pyglet.math.Vec2 = position
        self.color = color
        self.batch = batch
        self.group = group

        self.children = []
        self.parent = None
            
        self._depth = 0
        self._node_id = None # unique number assigned during traversal

        self.lines = {}
        self.lines["left"] = pyglet.shapes.Line( 0, 0, 1, 0, batch = self.batch, color = self.color )
        # self.lines["left"].opacity = 90
        self.lines["top"] = pyglet.shapes.Line( 0, 0, 1, 0, batch = self.batch, color = self.color )
        # self.lines["top"].opacity = 90
        self.lines["right"] = pyglet.shapes.Line( 0, 0, 1, 0, batch = self.batch, color = self.color )
        # self.lines["right"].opacity = 90
        self.lines["bottom"] = pyglet.shapes.Line( 0, 0, 1, 0, batch = self.batch, color = self.color )
        # self.lines["bottom"].opacity = 90


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
        # print("method: get_child_position %s"%this)
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


    def pprint_tree(self, depth : int = 0) -> None:
        self._depth = depth
        print("    "*depth, "%s ( %s )"%(depth, self._node_id), "'%s'"%self.name, type(self).__name__ )#, "window: %s"%self.window)
        print("    "*depth, "  > size:", self.get_available_size_from_parent(), "position:", self.get_position_from_parent() )
        for c in self.children:
            c.pprint_tree( depth+1 )

    
    def update( self, depth : int = 0, count : int = 0 ) -> None:
        """traverse all children and update all geometries etc"""
        self._depth = depth
        self._node_id = count
        count += 1
        self.get_available_size_from_parent()
        self.get_position_from_parent()

        margin = 5

        self.lines["left"].x = self.position[0] + margin
        self.lines["left"].y = self.position[1] + margin
        self.lines["left"].x2 = self.position[0] + margin
        self.lines["left"].y2 = self.position[1] + self.height - margin

        self.lines["top"].x = self.position[0] + margin
        self.lines["top"].y = self.position[1] + self.height - margin
        self.lines["top"].x2 = self.position[0] + self.width - margin
        self.lines["top"].y2 = self.position[1] + self.height - margin

        self.lines["right"].x = self.position[0] + self.width - margin
        self.lines["right"].y = self.position[1] + self.height -margin
        self.lines["right"].x2 = self.position[0] + self.width -margin
        self.lines["right"].y2 = self.position[1] + margin

        self.lines["bottom"].x = self.position[0] + margin
        self.lines["bottom"].y = self.position[1] + margin
        self.lines["bottom"].x2 = self.position[0] + self.width -margin
        self.lines["bottom"].y2 = self.position[1] + margin

        # _y = self._node_id * 20

        # self.lines["left"].x = 0 + depth * 15
        # self.lines["left"].y = _y
        # self.lines["left"].x2 = 0 + 15 + depth * 15
        # self.lines["left"].y2 = _y + 15

        # self.lines["top"].x = 15 + depth * 15
        # self.lines["top"].y = _y
        # self.lines["top"].x2 = 15 + 15 + depth * 15
        # self.lines["top"].y2 = _y + 15

        # self.lines["right"].x = 30 + depth * 15
        # self.lines["right"].y = _y
        # self.lines["right"].x2 = 30 + 15 + depth * 15
        # self.lines["right"].y2 = _y + 15

        # self.lines["bottom"].x = 45 + depth * 15
        # self.lines["bottom"].y = _y
        # self.lines["bottom"].x2 = 45 + 15 + depth * 15
        # self.lines["bottom"].y2 = _y + 15

        for c in self.children:
            count = c.update( depth+1, count )
        return count


    def draw(self):
        # maybe just draw a coloured outline
        # NO DRAW, ONLY BATCH.
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
            x = self.position[0] + int(self.width*self.ratio)
            y = self.position[1]
            return (x, y)



class VSplitContainer( SplitContainer ):
    """container managing split view of two child containers,
    first child added is on bottom, second child on top
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
            y = self.position[1] + int(self.height*self.ratio)
            return (x, y)


class ViewportContainer( Container ):
    """ Container that holds an openGL Viewport """
    def __init__(self,
            name="container",
            width : int = 128,
            height : int = 128,
            position : pyglet.math.Vec2 = pyglet.math.Vec2(),
            window : pyglet.window.Window = None,
            camera : boxer.camera.Camera = None,
            color = (255, 255, 255, 255),
            batch : pyglet.graphics.Batch = None,
            group : pyglet.graphics.Group = None
            ):
        Container.__init__(self,
            name = name,
            width = width,
            height = height,
            position = position,
            window = window,
            color = color,
            batch = batch,
            group = group,
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


    def add_child(self, child) -> None:
        raise("ViewportContainers cannot contain children")


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
    import pyglet.gl as gl
    sys.path.extend("..")
    import boxer.camera
    from pyglet import app

    win = pyglet.window.Window( width=960, height=540 )
    batch = pyglet.graphics.Batch()

    # container tree
    c = HSplitContainer(name="root_container", ratio=0.3333, window = win, batch = batch)
    c_l = Container(name = "left_panel", batch = batch)
    c.add_child( c_l )

    c_r = VSplitContainer(name= "right_panel", batch = batch, ratio = 0.333)
    c.add_child( c_r )

    c_r_one = Container(name="right_panel_bottom", batch = batch, color=(128, 255, 128, 128))
    c_r.add_child( c_r_one )
    c_r_two = Container( name="right_panel_top", batch = batch )
    c_r.add_child( c_r_two )

    c_fh = HSplitContainer(name="top_final_split", batch = batch, ratio = 0.25)
    c_r_two.add_child( c_fh )

    cfh_left = Container(name="infal_split_left", batch=batch, color=(255, 180, 10, 128))
    c_fh.add_child( cfh_left )

    cfh_right_vp = ViewportContainer(name="final_viewport", batch=batch, color=(255,255,255,255))
    c_fh.add_child( cfh_right_vp )

    # c_r = VSplitContainer( name = "right panel", ratio =0.55, batch = batch )
    # c.add_child( c_r )

    # c_tr = HSplitContainer(name="top_right_panel", ratio=0.85, batch = batch)
    # c_r.add_child( c_tr )
    # c_tr_1 = Container(name="topright_h1_panel", batch = batch)
    # c_tr.add_child(c_tr_1)
    # c_tr_2 = Container(name="topright_h2_panel", batch = batch)
    # c_tr.add_child(c_tr_2)

    # c_vp = ViewportContainer(name="viewport_panel", batch = batch, color = (255, 20, 20, 255) )
    # c_r.add_child( c_vp )

    c.update(count = 0)
    c.pprint_tree()

    @win.event
    def on_draw():
        win.clear()
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        batch.draw()

    app.run()