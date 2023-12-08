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
        self.lines["top"] = pyglet.shapes.Line( 0, 0, 1, 0, batch = self.batch, color = self.color )
        self.lines["right"] = pyglet.shapes.Line( 0, 0, 1, 0, batch = self.batch, color = self.color )
        self.lines["bottom"] = pyglet.shapes.Line( 0, 0, 1, 0, batch = self.batch, color = self.color )


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
            # likely a Container 
            ps = self.parent.get_child_size( self )
            self.width = ps[0]
            self.height = ps[1]
            return (self.width, self.height)
        elif self.parent == None:
            # maybe it's a pyglet.window.Window ? 
            ws = self.window.get_size()
            self.width = ws[0]
            self.height = ws[1]
            return (self.width, self.height)#
        else:
            return (None, None)


    def get_child_position(self, this):
        return self.position


    def get_position_from_parent( self ) -> tuple:
        if hasattr(self.parent, "get_child_position"):
            # likely a Container
            self.position = self.parent.get_child_position( self )
            return self.position
        elif self.parent == None:
            # waybe its a pyglet.window.Window ?
            self.position = (0,0)
            return self.position
        else:
            return (None, None)


    @ property
    def child_count(self):
        return len(self.children)


    def pprint_tree(self, depth : int = 0) -> None:
        """prety prints the structure, indented by depth"""
        self._depth = depth
        print("    "*depth, "%s ( %s )"%(depth, self._node_id), "'%s'"%self.name, type(self).__name__ )#, "window: %s"%self.window)
        print("    "*depth, "  > size:", self.get_available_size_from_parent(), "position:", self.get_position_from_parent() )
        for c in self.children:
            c.pprint_tree( depth+1 )

    
    def update( self, depth : int = 0, count : int = 0 ) -> None:
        """traverse all children and update all geometries, positions, etc"""
        self._depth = depth
        self._node_id = count
        count += 1
        self.get_available_size_from_parent()
        self.get_position_from_parent()

        margin = 3

        self.lines["left"].x = self.position[0] + margin
        self.lines["left"].y = self.position[1] + margin
        self.lines["left"].x2 = self.position[0] + margin
        self.lines["left"].y2 = self.position[1] + self.height - margin

        self.lines["top"].x = self.position[0] + margin -1
        self.lines["top"].y = self.position[1] + self.height - margin
        self.lines["top"].x2 = self.position[0] + self.width - margin
        self.lines["top"].y2 = self.position[1] + self.height - margin

        self.lines["right"].x = self.position[0] + self.width - margin
        self.lines["right"].y = self.position[1] + self.height - margin
        self.lines["right"].x2 = self.position[0] + self.width - margin
        self.lines["right"].y2 = self.position[1] + margin + 1

        self.lines["bottom"].x = self.position[0] + margin
        self.lines["bottom"].y = self.position[1] + margin
        self.lines["bottom"].x2 = self.position[0] + self.width -margin
        self.lines["bottom"].y2 = self.position[1] + margin

        for c in self.children:
            count = c.update( depth+1, count )
        return count


    def draw(self):
        # maybe just draw a coloured outline
        # NO DRAW, ONLY BATCH.
        pass


# ------------------------------------------------------------------------------
# Container events
Container.register_event_type("mouse_entered")
Container.register_event_type("mouse_exited")
Container.register_event_type("resized")
Container.register_event_type("split")
Container.register_event_type("collapsed")
# ------------------------------------------------------------------------------


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
            return (math.floor(self.width*self.ratio), self.height )
        else:
            return (math.ceil(self.width*(1-self.ratio)), self.height )


    def get_child_position(self, this) -> tuple:
        if this == self.children[0]:
            x = self.position[0]
            y = self.position[1]
            return (x, y)
        else:
            x = self.position[0] + math.floor(self.width*self.ratio)
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
            return (self.width , math.floor(self.height * self.ratio) )
        else:
            return (self.width , math.ceil(self.height * (1.0 - self.ratio)) )


    def get_child_position(self, this) -> tuple:
        if this == self.children[0]:
            x = self.position[0]
            y = self.position[1]
            return (x, y)
        else:
            x = self.position[0]
            y = self.position[1] + math.floor(self.height*self.ratio)
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

        # camera
        if not camera:
            print("if not self.camera %s"%self.window)
            print(type(self.window))
            camera = boxer.camera.get_default_camera( self.window )
        self.camera = camera


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
    import boxer.shaping
    from pyglet import app
    from time import perf_counter
    import math



    win = pyglet.window.Window( width=960, height=540 )
    batch = pyglet.graphics.Batch()

    # container tree
    c = HSplitContainer(name="root_container", ratio=0.36, window = win, batch = batch)
    c_l = Container(name = "left_panel", batch = batch)
    c.add_child( c_l )

    c_r = VSplitContainer(name= "right_panel", batch = batch, ratio = 0.333,color=(128,128,255,0))
    c.add_child( c_r )

    c_r_one = Container(name="right_panel_bottom", batch = batch, color=(128, 255, 128, 128))
    c_r.add_child( c_r_one )
    # c_r_two = Container( name="right_panel_top", batch = batch )
    # c_r.add_child( c_r_two )

    c_fh = HSplitContainer(name="top_final_split", batch = batch, ratio = 0.05, color=(128,128,255,0))
    c_r.add_child( c_fh )

    cfh_left = VSplitContainer(name="final_split_left", batch=batch, color=(128,128,255,0))#, color=(255, 180, 10, 128))
    c_fh.add_child( cfh_left )

    cfh_left_top = Container(name ="final_split_left_up", batch=batch, color=(255, 180, 10, 128))
    cfh_left.add_child(cfh_left_top)

    cfh_left_top = Container(name ="final_split_left_down", batch=batch, color=(255, 180, 10, 128))
    cfh_left.add_child(cfh_left_top)

    cfh_right_vp = ViewportContainer(name="final_viewport", batch=batch, color=(255,255,255,128))
    c_fh.add_child( cfh_right_vp )

    t1_start = perf_counter()
    c.update(count = 0)
    t1_stop = perf_counter()

    c.pprint_tree()

    # ---------------
    print("time to 'update': %s"%( t1_stop - t1_start ))

    gtime = 0.0
    ss1 = 1.0
    ss2 = 1.0
    ss3 = 1.0

    @win.event
    def on_draw():
        global gtime, ss1, ss2, ss3
        gtime += 0.02
        ss1 = boxer.shaping.remap(math.sin( gtime *0.05 ), -1.0, 1.0, 0.2, 0.52)
        ss2 = boxer.shaping.remap(math.sin( gtime * .2 + .7447), -1.0, 1.0, 0.2, 0.82)
        ss3 = boxer.shaping.remap(math.sin( gtime * .9 + -.7447), -1.0, 1.0, 0.05, 0.15)
        c.ratio = ss1
        c_r.ratio = ss2
        c_fh.ratio = ss3

        c.update()

        win.clear()
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        batch.draw()

    app.run()