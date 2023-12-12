"""heirarchical Containers for a forms-like structure.
For building windowareas and partitions et cetera.
"""
import math

# ui containers
if __name__ == "__main__":
    import sys
    sys.path.extend("..")

import pyglet
import pyglet.gl as gl
import pyglet.graphics
import pyglet.shapes
import boxer.camera
import boxer.shapes

import imgui

# https://www.reddit.com/r/learnprogramming/comments/214nd9/making_a_gui_from_scratch/
# https://developer.valvesoftware.com/wiki/VGUI_Documentation

class Container( pyglet.event.EventDispatcher ):
    """
    Create a tree of Containers by adding children.
    
    c = Container(name="root_container", window=window)
    c.add_child(name="child_container", Container(window=window) )
    
    Add SplitContainers to divide a container into two child areas with a split ratio control.

    Adding children to a parent connects the child to the parent window.

    If window dimensions or parent dimensions change (inc. split ratios or other constraints),
    call `.update_geometries()` on a node to update all descendant dimensions.

    `.update_structure()` needs to be called if the tree structure changes due
    to adding or collapsing children.
    This updates node depths, unique id and identifies leaves in the tree.

    The tree leaves are connected to the window's `on_mouse` events.
    """
    def __init__(self,
            name="container",
            window : pyglet.window.Window = None,
            width : int = 128,
            height : int = 128,
            use_explicit_dimensions : bool = False,
            position : pyglet.math.Vec2 = pyglet.math.Vec2(),
            color = (255, 255, 255, 60),
            batch : pyglet.graphics.Batch = None,
            group : pyglet.graphics.Group = None,
            ):

        self.name = name
        self.window = window
        print("self.window: %s"%str(self.window))
        self.width = width
        self.height = height
        self.position : pyglet.math.Vec2 = position
        self.use_explicit_dimensions = use_explicit_dimensions 
        self.color = color
        self.batch = batch
        self.group = group

        self.children = []
        self.parent = None
        self.leaves = []
        self.is_leaf = False

        self.mouse_inside = False

        self._depth = 0
        self._node_id = None # unique number assigned during traversal

        self.lines = {}
        self.lines["left"] = pyglet.shapes.Line( 0, 0, 1, 0,
                                            batch = self.batch,
                                            color = self.color )
        self.lines["top"] = pyglet.shapes.Line( 0, 0, 1, 0,
                                            batch = self.batch,
                                            color = self.color )
        self.lines["right"] = pyglet.shapes.Line( 0, 0, 1, 0,
                                            batch = self.batch,
                                            color = self.color )
        self.lines["bottom"] = pyglet.shapes.Line( 0, 0, 1, 0,
                                            batch = self.batch,
                                            color = self.color )

        self._lines_original_color = self.color

        self.debug_label_name = pyglet.text.Label(self.name,
                        font_size=8,
                        x=0.0, y=0.0,
                        anchor_x='left', anchor_y='top',
                        batch=batch,
                        color=( 255, 255, 255, 50 ),
                        width = 100,
                        multiline=True,)


    def add_child(self, child) -> None:
        """add a child to this Container"""
        if child not in self.children:
            child.parent = self
            child.window = self.window
            # child.connect_to_window_mouse_events( child.window )
            self.children.append( child )


    def get_child_size(self, this) -> tuple:
        """calculate the width and height available for a child
        ('this' is normally self!)
        subclasses should override this method for their own caclulations
        """
        return (self.width, self.height)


    def get_available_size_from_parent( self ) -> tuple:
        """ask parent for available size"""
        if self.use_explicit_dimensions:
            # do not modify size
            return (self.width, self.height)
        if hasattr(self.parent, "get_child_size"):
            # likely a Container 
            ps = self.parent.get_child_size( self )
            self.width = ps[0]
            self.height = ps[1]
            return (self.width, self.height)
        if self.parent is None:
            # maybe it's a pyglet.window.Window ?
            # if not do not modify dimensions
            if self.window:
                ws = self.window.get_size()
                self.width = ws[0]
                self.height = ws[1]
            return (self.width, self.height)
        return (None, None)


    def get_child_position(self, this):
        """the function that a child node will ask self for a position
        to place the child"""
        return self.position


    def get_position_from_parent( self ) -> tuple:
        """ask this node's parennt of a position to place self"""
        if self.use_explicit_dimensions:
            # do not modify position
            return self.position
        if hasattr(self.parent, "get_child_position"):
            # likely a Container
            self.position = self.parent.get_child_position( self )
            return self.position
        if self.parent is None:
            # maybe its a pyglet.window.Window ?
            if self.window and not self.use_explicit_dimensions:
                self.position = (0,0)
            return self.position
        return (None, None)


    @ property
    def child_count(self):
        """return the number of children"""
        return len(self.children)


    def pprint_tree(self, depth : int = 0) -> None:
        """prety prints the structure, indented by depth"""
        self._depth = depth
        print("    "*depth, "%s (id: %s )"%(depth, self._node_id), "'%s'"%self.name, type(self).__name__ )#, "window: %s"%self.window)
        print("    "*depth, "  > size:", self.get_available_size_from_parent(), "position:", self.get_position_from_parent() )
        for child in self.children:
            child.pprint_tree( depth+1 )


    def update_geometries( self ) -> None:
        """traverse all children and update all geometries, positions, etc"""
        self.get_available_size_from_parent()
        self.get_position_from_parent()

        margin = 0#3

        self.debug_label_name.x = self.position[0] + 5
        self.debug_label_name.y = self.position[1] + self.height - 2
        self.debug_label_name.text =\
            self.name +\
            "\n.is_leaf " +\
            str(self.is_leaf) +\
            "\n.mouse_inside " +\
            str(self.mouse_inside)

        if self.is_leaf:
            self.debug_label_name.opacity = 50
        else:
            self.debug_label_name.opacity = 0

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

        if self.mouse_inside:
            for lk in self.lines.items(): #self.lines.keys():
                # self.lines[lk].width = 3
                lk[1].width = 0.5#1.5
                lk[1].opacity = 255
        else:
            for lk in self.lines.items():#keys():
                lk[1].width = .5
                lk[1].opacity = self._lines_original_color[3]
                # self.lines[lk].width = 1

        for child in self.children:
            child.update_geometries()


    def update_structure( self, depth : int = 0, count : int = 0, leaves : list = list() ) -> int:
        """Update internal structure data, like is_leaf, unique ids, pushing and
        popping events handlers.
        Call this after adding or removing or replacing children of the tree."""

        self._depth = depth
        self._node_id = count
        count += 1

        if len(self.children) == 0:
            self.is_leaf = True
            leaves.append( self )
            # TODO: pushed mouse handlers --------------------------------------
            if self.window:
                self.window.push_handlers(on_mouse_motion=self.on_mouse_motion)
            # ------------------------------------------------------------------
        else:
            self.is_leaf = False
            self.mouse_inside = False
            # TODO: popped mouse handlers --------------------------------------
            if self.window:
                self.window.remove_handlers(on_mouse_motion=self.on_mouse_motion)
            # ------------------------------------------------------------------
            for child in self.children:
                count, leaves = child.update_structure( depth+1, count, leaves )
        return count, leaves


    def update(self) -> None:
        """update both geometries and structure
        
        calls
        self.update_structure()
        self.update_geometries()
        """
        self.update_structure()
        self.update_geometries()


    def draw(self):
        """future draw method"""
        # maybe just draw a coloured outline
        # NO DRAW, ONLY BATCH.
        # if self.is_leaf:
        #     imgui.new_frame()
        #     imgui.render()
        #     imgui.end_frame()


    def on_mouse_motion(self, x, y, ds, dy) -> None:
        """to be bound to a pyglet.window.Window's mouse events"""
        if boxer.shapes.point_in_box( x, y,
                self.position[0],
                self.position[1],
                self.position[0]+self.width,
                self.position[1]+self.height ):
            if self.mouse_inside is not True:
                self.dispatch_event( "mouse_entered", self )
            self.mouse_inside = True
        else:
            if self.mouse_inside is True:
                self.dispatch_event( "mouse_exited", self )
            self.mouse_inside = False


# ------------------------------------------------------------------------------
# Container events
Container.register_event_type("mouse_entered")
Container.register_event_type("mouse_exited")
Container.register_event_type("resized") #      TODO
Container.register_event_type("split") #        TODO
Container.register_event_type("collapsed") #    TODO
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
            return (math.floor(self.width*self.ratio) -1 , self.height  )
        else:
            return (math.ceil(self.width*(1-self.ratio)), self.height  )


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
            return (self.width , math.floor(self.height * self.ratio) -1 )
        else:
            return (self.width , math.ceil(self.height * (1.0 - self.ratio))  )


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
            use_explicit_dimensions : bool = False,
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
            use_explicit_dimensions = use_explicit_dimensions,
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
        """pop the camera from the viewport transform"""
        self.camera.pop()


    def add_child(self, child) -> None:
        raise("ViewportContainers cannot contain children")


    # def draw(self) -> None:
    #     # draw the viewport box
    #     # draw viewport ornaments
    #     # draw viewport GUI widgets, TODO: Viewport Widgets
    #     pass



# ------------------------------------------------------------------------------
if __name__ == "__main__":
    print("run containers.py main:")

    import sys
    # import pyglet.gl as gl
    sys.path.extend("..")
    # import boxer.camera
    import pyglet.window
    from pyglet import app
    import boxer.shaping
    from time import perf_counter
    # import math

    _window_config = gl.Config(
        sample_buffers = 1,
        samples = 1,#16,
        depth_size = 16,
        double_buffer = True,
    )

    win = pyglet.window.Window( width=960, height=540, config=_window_config )
    line_batch = pyglet.graphics.Batch()

    # test container events:
    def mouse_entered_container( container ) -> None:
        """test"""
        print("--> mouse entered %s"%container.name)

    def mouse_exited_container( container ) -> None:
        """test"""
        print("o-- mouse exited %s"%container.name)

    # container tree
    #c = HSplitContainer(name="root_container", ratio=0.36, window = win, batch = line_batch)
    c = HSplitContainer(name="root_container",
                        ratio=0.36,
                        window = win,
                        batch = line_batch,
                        position=pyglet.math.Vec2(50,50),
                        width= 320,
                        height=320,
                        use_explicit_dimensions=True)
    c.push_handlers( mouse_entered = mouse_entered_container )
    c.push_handlers( mouse_exited = mouse_exited_container )

    c_l = Container(name = "left_panel", batch = line_batch)
    c_l.push_handlers( mouse_entered = mouse_entered_container )
    c_l.push_handlers( mouse_exited = mouse_exited_container )
    c.add_child( c_l )

    c_r = VSplitContainer(name= "right_panel", batch = line_batch, ratio = 0.333,color=(128,128,255,0))
    c_r.push_handlers( mouse_entered = mouse_entered_container )
    c_r.push_handlers( mouse_exited = mouse_exited_container )
    c.add_child( c_r )

    c_r_one = Container(name="right_panel_bottom", batch = line_batch, color=(128, 255, 128, 128))
    c_r_one.push_handlers( mouse_entered = mouse_entered_container )
    c_r_one.push_handlers( mouse_exited = mouse_exited_container )
    c_r.add_child( c_r_one )

    c_fh = HSplitContainer(name="top_final_split", batch = line_batch, ratio = 0.65, color=(128,128,255,0))
    c_fh.push_handlers( mouse_entered = mouse_entered_container )
    c_fh.push_handlers( mouse_exited = mouse_exited_container )
    c_r.add_child( c_fh )

    cfh_left = VSplitContainer(name="final_split_left", batch=line_batch, color=(128,128,255,0))#, color=(255, 180, 10, 128))
    cfh_left.push_handlers( mouse_entered = mouse_entered_container )
    cfh_left.push_handlers( mouse_exited = mouse_exited_container )
    c_fh.add_child( cfh_left )

    cfh_left_bottom = Container(name ="final_split_left_bottom", batch=line_batch, color=(255, 180, 10, 128))
    cfh_left_bottom.push_handlers( mouse_entered = mouse_entered_container )
    cfh_left_bottom.push_handlers( mouse_exited = mouse_exited_container )
    cfh_left.add_child(cfh_left_bottom)

    cfh_left_top = Container(name ="final_split_left_top", batch=line_batch, color=(255, 180, 10, 128))
    cfh_left_top.push_handlers( mouse_entered = mouse_entered_container )
    cfh_left_top.push_handlers( mouse_exited = mouse_exited_container )
    cfh_left.add_child(cfh_left_top)

    cfh_right_vp = ViewportContainer(name="final_viewport", batch=line_batch, color=(255,255,255,128))
    cfh_right_vp.push_handlers( mouse_entered = mouse_entered_container )
    cfh_right_vp.push_handlers( mouse_exited = mouse_exited_container )
    c_fh.add_child( cfh_right_vp )

    t1_start = perf_counter()
    count, leaves = c.update_structure()
    c.update_geometries()#count = 0)
    t1_stop = perf_counter()

    c.pprint_tree()

    print("leaves:")
    for leaf in leaves:
        print("    %s"%leaf.name)

    # ---------------
    print("time to 'update': %s"%( t1_stop - t1_start ))

    gtime = 0.0
    ss1 = 1.0
    ss2 = 1.0
    ss3 = 1.0
    ss4 = 1.0


    @win.event
    def on_resize( width, height ):
        """resize"""
        print("on_resize (%s, %s)"%(width, height))
        c.update_geometries()

    @win.event
    def on_draw():
        """draw"""
        # global gtime, ss1, ss2, ss3
        # gtime += 0.02
        # ss1 = boxer.shaping.remap(math.sin( gtime *0.05 ), -1.0, 1.0, 0.2, 0.52)
        # ss2 = boxer.shaping.remap(math.sin( gtime * .2 + .7447), -1.0, 1.0, 0.2, 0.82)
        # ss3 = boxer.shaping.remap(math.sin( gtime * .9 + -.7447), -1.0, 1.0, 0.45, 0.5)
        # ss4 = boxer.shaping.remap(math.sin( gtime * 1.6 + -1.656), -1.0, 1.0, 0.3, 0.7)
        # c.ratio = ss1
        # c_r.ratio = ss2
        # c_fh.ratio = ss3
        # cfh_left.ratio = ss4

        c.update_geometries()

        win.clear()
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        line_batch.draw()
        for l in leaves:
            l.draw()
    app.run()