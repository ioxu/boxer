"""heirarchical Containers for a forms-like structure.
For building windowareas and partitions et cetera.

The root container must be a Container (non-SplitContainer-type)
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

    `.update_structure()` aneeds to be called if the tree structure changes due
    to adding or collapsing children.
    This updates node depths, unique id and identifies leaves in the tree.
    This also updates pushing and popping handlers to subscribers of container events.

    `.update()` can be called to invoke both `.update_geometries()` and `.update_structure()`

    The tree leaves are connected to the window's `on_mouse` events.
    """

    cog_image = pyglet.image.load("boxer/resources/cog_16.png")
    window_image = pyglet.image.load("boxer/resources/window_16.png")
    textures = {
        "cog" : cog_image.get_texture(),
        "window" : window_image.get_texture(),
    }

    container_view_types = ["graph", "3d", "parameters", "spreadsheet", "python", "log"]

    # TODO: replace these ACTION constants/lables with enum.Enum type?
    container_action_labels = [\
                            "split horizontal",
                            "split vertical",
                            "close",
                            "close split",
                            "close others"]
    
    ACTION_SPLIT_HORIZONTAL = 0     # split this container into a HSplitContainer with two child Containers.
    ACTION_SPLIT_VERTICAL = 1       # split this container into a VSplitCOntainer with two child Containers.
    ACTION_CLOSE = 2                # close this container, if in a split container convert the split to a single.
    ACTION_CLOSE_SPLIT = 3          # replace the parent SplitContainer with this one.
    ACTION_CLOSE_OTHERS = 4         # close all other containers, leaving this one.


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
        # print("self.window: %s"%str(self.window))
        self.width = width
        self.height = height
        self.position : pyglet.math.Vec2 = position
        self.use_explicit_dimensions = use_explicit_dimensions 
        self.color = color
        self.batch = batch
        self.group = group

        self.children = []
        self.parent = None

        # usually just the root container would hold an updated list of leaves.
        # container.update() sets this on whatever container update() is called on.
        # usually update a tree with container.get_root_container().update()
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
                        color=( 255, 255, 255, 50),
                        width = 100,
                        multiline=True,)

        # imgui
        self.container_view_combo_selected = 0
        self.container_actions_combo_selected =0


    def __repr__(self):
        return "%s at %s name:'%s'"%(type(self), id(self),self.name)


    def add_child(self, child) -> None:
        """add a child to this Container"""
        if child not in self.children:
            child.parent = self
            child.window = self.window
            # child.connect_to_window_mouse_events( child.window )
            self.children.append( child )


    def remove_children(self, old_children = None) -> list:
        """clear all children"""
        # WTF, argument of a static mutable, never realised it before:
        # https://stackoverflow.com/questions/1132941/least-astonishment-and-the-mutable-default-argument

        if old_children is None:
            old_children = []

        old_children = self.children + old_children
        for child in self.children:
            if child is not None:
                child.parent = None
                idx = self.children.index( child )
                self.children[idx] = None
    
                if child.window:
                    # self.window.remove_handlers(on_mouse_motion=child.on_mouse_motion)
                    child.window.remove_handlers(on_mouse_motion=child.on_mouse_motion)
                    child.remove_handlers( )
                    child.window = None
                child.remove_children( old_children )
  
        self.children=[]
        return old_children


    def remove_child(self, child ):
        """remove a child from children list
        `return`
            `index` : `int` : index of removed child
        """
        idx = None
        if child in self.children:
            child.parent = None
            child.window = None
            idx = self.children.index( child )
            if self.window:
                self.window.remove_handlers(on_mouse_motion=child.on_mouse_motion)
                self.remove_handlers( )
            self.children[idx] = None
        return idx


    def set_child(self, child, index=0) -> None:
        """sets a child to a specific child index
        if the index > len(self.children) the children list is extended by Nones
        to length.
        """
        if len(self.children) <= index:
            # extend list to length==(index+1)
            self.children.extend( [None] * ( index + 1 - len(self.children) ))
        child.parent = self
        child.window = self.window
        self.children[index] = child


    def replace_child(self, old_child, new_child ):
        """replace a child in children by new_child
        
        `returns:`
            idx `int or None` : index of replaced child or None
        """
        idx = None
        if old_child in self.children:
            idx = self.remove_child(old_child)
            if idx is not None:
                self.set_child( new_child, idx )
        return idx


    def replace_by( self, new_container ) -> None:
        """either replace self in the parents' children
        OR
        return a configured copy
        
        must always get the return value, eg:
        `container = container.replace_by( new_container )`
        """
        # TODO: adressing #2
        parent = self.parent
        this_container = self
        if parent:
            parent.replace_child( self, new_container )
            return new_container
        else:
            new_container.use_explicit_dimensions = self.use_explicit_dimensions
            new_container.position = self.position
            new_container.width = self.width
            new_container.height = self.height
            new_container.window = self.window
            return new_container


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


    def get_root_container(self):
        """scans up to find rootiest node"""
        # print("get root container %s"%self.name)
        if self.parent == None:
            return self
        return self.parent.get_root_container()


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

        margin = 1#3

        self.debug_label_name.x = self.position[0] + 5
        self.debug_label_name.y = self.position[1] + self.height - 2 - 15
        self.debug_label_name.text =\
            self.name + " (%s)"%(type(self).__name__) +\
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

        self.lines["top"].x = self.position[0] + margin #-1
        self.lines["top"].y = self.position[1] + self.height - margin
        self.lines["top"].x2 = self.position[0] + self.width - margin
        self.lines["top"].y2 = self.position[1] + self.height - margin

        self.lines["right"].x = self.position[0] + self.width - margin
        self.lines["right"].y = self.position[1] + self.height - margin
        self.lines["right"].x2 = self.position[0] + self.width - margin
        self.lines["right"].y2 = self.position[1] + margin #+ 1

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
            if self.is_leaf:
                for lk in self.lines.items():#keys():
                    lk[1].width = .5
                    lk[1].opacity = self._lines_original_color[3]
                    # self.lines[lk].width = 1
            else:
                for lk in self.lines.items():
                    lk[1].opacity = 0

        for child in [c for c in self.children if c is not None]:
            child.update_geometries()


    #def update_structure( self, depth : int = 0, count : int = 0, leaves : list = list() ) -> int:
    def update_structure( self, depth : int = 0, count : int = 0, leaves = None ) -> int:
        """Update internal structure data, like is_leaf, unique ids, pushing and
        popping events handlers.
        Push and pop handlers to additional subscribers.
        Call this after adding or removing or replacing children of the tree.
        """
        if leaves is None:
            leaves = []

        self._depth = depth
        self._node_id = count
        count += 1

        # ----------------------------------------------------------------------
        # remove all handlers first?
        # TODO: how to parameterise functions to pop handlers from #3 @ioxu
        if self.window:
            self.window.remove_handlers(on_mouse_motion=self.on_mouse_motion)
            self.remove_handlers( mouse_entered = mouse_entered_container )
            self.remove_handlers( mouse_exited = mouse_exited_container )
        # ----------------------------------------------------------------------

        if len(self.children) == 0:
            self.is_leaf = True
            leaves.append( self )
            # add handers for leaves -------------------------------------------
            # TODO: how to parameterise functions to push handlers to #3 @ioxu
            if self.window:
                self.window.push_handlers(on_mouse_motion=self.on_mouse_motion)
                self.push_handlers( mouse_entered = mouse_entered_container )
                self.push_handlers( mouse_exited = mouse_exited_container )
            # ------------------------------------------------------------------
        else:
            self.is_leaf = False
            self.mouse_inside = False
            if self in leaves:
                leaves.remove(self)

            for child in self.children:
                count, leaves = child.update_structure( depth+1, count, leaves )
        return count, leaves


    def update(self) -> None:
        """update both geometries and structure
        
        calls
        self.update_structure()
        self.update_geometries()
        """
        # self.leaves = []
        # _, self.leaves = self.update_structure(leaves=self.leaves)
        _, self.leaves = self.update_structure()
        self.update_geometries()


    def draw(self):
        """future draw method"""
        # maybe just draw a coloured outline
        # NO DRAW, ONLY BATCH.

        # ----------------------------------------------------------------------
        # TODO: work out why this happens
        # something about when ACTION_CLOSE_OTHERS and/or
        # recursive .remove_children() removes a child that
        # is stil in the list of .leaves being drawn in main loop
        if self.window is None:
            print("DRAW: %s .window is None"%self)
            return
        # ----------------------------------------------------------------------


        pos = self.position

        # imgui ----------------------------------------------------------------
        # no decoration / no collapsible title bar
        container_imwindow_flags = imgui.WINDOW_NO_TITLE_BAR\
                            | imgui.WINDOW_NO_BACKGROUND\
                            | imgui.WINDOW_NO_RESIZE\
                            | imgui.WINDOW_NO_SAVED_SETTINGS\
                            | imgui.WINDOW_NO_SCROLLBAR

        # with title bar
        container_imwindow_flags2 = imgui.WINDOW_NO_BACKGROUND\
                            | imgui.WINDOW_NO_RESIZE\
                            | imgui.WINDOW_NO_SAVED_SETTINGS


        imgui.set_next_window_position(\
                            pos[0],
                            self.window.height - pos[1] - self.height)
        imgui.set_next_window_size(\
                            self.width-1,
                            self.height)

        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING , imgui.Vec2(0.0, 0.0))
        with imgui.begin(self.name, flags = container_imwindow_flags ) as imgui_window:
            imgui.push_clip_rect(\
                            pos[0],
                            self.window.height - pos[1] - self.height,
                            pos[0] + self.width -1,
                            self.window.height - pos[1] - 1)
            imgui.push_style_var(imgui.STYLE_FRAME_PADDING, imgui.Vec2(1.0, 1.0))
            imgui.push_style_var(imgui.STYLE_ITEM_SPACING, imgui.Vec2(0.0, 0.0))
            imgui.image_button( self.textures["cog"].id, 12, 12)
            imgui.same_line()
            imgui.image_button( self.textures["window"].id, 12, 12)
            imgui.same_line()
            
            imgui.push_item_width(80)

            # combo ------------------------------------------------------------
            if imgui.begin_combo(\
                            "##view combo",
                            Container.container_view_types[self.container_view_combo_selected],
                            flags = imgui.COMBO_NO_PREVIEW):
                imgui.push_style_var(imgui.STYLE_ITEM_SPACING, imgui.Vec2(3.0, 3.0))
                for i, item in enumerate(Container.container_view_types):
                    is_selected = (i==self.container_view_combo_selected)
                    if imgui.selectable( item, is_selected )[0]:
                        self.container_view_combo_selected = i
                    if is_selected:
                        imgui.set_item_default_focus()
                imgui.pop_style_var(1)
                imgui.end_combo()
            # ------------------------------------------------------------------
            imgui.pop_item_width()

            imgui.same_line()
            imgui.text(self.name)

            imgui.set_cursor_pos( (self.width - 15, 0) )
            
            # container action combo -------------------------------------------
            do_container_action = False
            action_item_hovered = None
            do_draw_container_action_hint = False
            if imgui.begin_combo(\
                        "##action combo",
                        Container.container_action_labels[self.container_actions_combo_selected],
                        flags = imgui.COMBO_NO_PREVIEW):
                imgui.push_style_var(imgui.STYLE_ITEM_SPACING, imgui.Vec2(3.0, 3.0))
                for i2, item2 in enumerate(Container.container_action_labels):

                    
                    if i2 == 2:
                        # add a seperator after two items
                        imgui.separator()
                    if imgui.selectable( item2, selected = False )[0]:
                        self.container_actions_combo_selected = i2
                        print("container action: '%s' (%s)"%(\
                                    Container.container_action_labels[self.container_actions_combo_selected],
                                    self.name))
                        do_container_action = True
                    if imgui.is_item_hovered():
                        action_item_hovered = i2
                        # print( "HOVERED %s:'%s' (on '%s')"%(action_item_hovered,Container.container_action_labels[action_item_hovered], self.name) )
                        do_draw_container_action_hint = True


                imgui.pop_style_var(1)
                imgui.end_combo()

            # ------------------------------------------------------------------

            imgui.pop_style_var(2)
            imgui.pop_clip_rect()
        imgui.pop_style_var()

        if do_container_action:
            print(self.container_actions_combo_selected)
            # change_container( self, Container.container_action_labels[self.container_actions_combo_selected] )
            change_container( self, self.container_actions_combo_selected )

        if do_draw_container_action_hint:
            #draw_container_action_hint(  )
            # print( "DO HINT %s:'%s' (on '%s')"%(action_item_hovered,Container.container_action_labels[action_item_hovered], self.name) )
            match action_item_hovered:
                case Container.ACTION_SPLIT_HORIZONTAL:
                    # print("hsplit")
                    _x = self.position[0] + int(self.width/2.0)
                    pyglet.shapes.Line( _x, self.position[1], _x, self.position[1]+self.height, batch=None, color=(255,0,0,180)  ).draw()
                case Container.ACTION_SPLIT_VERTICAL:
                    # print("vsplit")
                    _y = self.position[1] + int(self.height/2.0)
                    pyglet.shapes.Line( self.position[0], _y, self.position[0] + self.width, _y, batch=None, color=(255,0,0,180)  ).draw()


    def on_mouse_motion(self, x, y, ds, dy) -> None:
        """to be bound to a pyglet.window.Window's mouse events"""
        if boxer.shapes.point_in_box( x, y,
                self.position[0],
                self.position[1],
                self.position[0]+self.width,
                self.position[1]+self.height ):
            if self.mouse_inside is not True:
                ret = self.dispatch_event( "mouse_entered", self )
                # print("dispatch event 'mouse_entered' for %s: return: %s"%(self.name, ret))
            self.mouse_inside = True
        else:
            if self.mouse_inside is True:
                ret = self.dispatch_event( "mouse_exited", self )
                # print("dispatch event 'mouse_exited' for %s: return: %s"%(self.name, ret))
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
            create_default_children : bool = False,
            **kwargs):
        Container.__init__( self, **kwargs )
        self.ratio = ratio
        self.create_default_children = create_default_children
        if self.create_default_children:
            self._default_children()

    def _default_children( self ):
        """generates default children
        for SplitContainer (a half abstract class) this will generate two children
        This method should be overwritten in subclasses
        """
        c1 = Container(name = self.name + "_cone", batch=self.batch, window=self.window)
        c2 = Container(name = self.name + "_ctwo", batch=self.batch, window=self.window)
        self.set_child( c1, 0 )
        self.set_child( c2, 1 )


class HSplitContainer( SplitContainer ):
    """container managing split view of two child containers,
    first child added is on left, second child on right
    """
    def __init__(self, **kwargs):
        SplitContainer.__init__( self, **kwargs )


    def _default_children(self):
        c1 = Container(name = self.name + "_cleft", batch=self.batch, window=self.window)
        c2 = Container(name = self.name + "_cright", batch=self.batch, window=self.window)
        self.set_child( c1, 0 )
        self.set_child( c2, 1 )


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


    def _default_children(self):
        c1 = Container(name = self.name + "_cbottom", batch=self.batch, window=self.window)
        c2 = Container(name = self.name + "_ctop", batch=self.batch, window=self.window)
        self.set_child( c1, 0 )
        self.set_child( c2, 1 )


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
def draw_container_tree_info( root : Container ) -> None:
    """draws a new imgui window with Container information
    expects tree to be initiaised with Container.update_structure() (?)
    """
    imgui.begin("Container info (%s)"%root.name,
                flags = imgui.WINDOW_NO_SAVED_SETTINGS)

    _tree_info_preorder(root)

    imgui.end()


def _tree_info_preorder(root) -> None:
    """preorder recursive tree walk"""
    if root is None:
        return

    # tree item colours
    c = (10.0, 10.0, 10.0, 1.0)
    if root.mouse_inside:
        c = c
    elif root.is_leaf:
        c = (0.6, 0.35, 0.02, 1.0)
    else:
        c = (0.4, 0.4, 0.4, 1.0)

    # draw tree
    imgui.push_font(font_default_bold)
    imgui.push_style_color( imgui.COLOR_TEXT, *c)
    if imgui.tree_node(root.name, imgui.TREE_NODE_DEFAULT_OPEN):
        c = (*c[:3], c[3]*0.5)
        imgui.push_font(font_small)
        imgui.push_style_color( imgui.COLOR_TEXT, *c )
        c = imgui.get_style(  )
        imgui.text("%s"%type(root).__name__)
        imgui.text("size: %s %s  pos: %s %s"%(root.width, root.height, root.position[0], root.position[1]))
        imgui.pop_style_color()
        imgui.pop_font()
        for c in root.children:
            _tree_info_preorder(c)    
        imgui.tree_pop()
    imgui.pop_font()
    imgui.pop_style_color(1)


def change_container( container, action ):
    """invoked from gui option to split or close containers, or operate an action upon a container
    `args`:
        `container` : `Container` -  the container to operate on
        `action` : `int` - container action, a Container.ACTION_* constant
    """

    match action:
        case Container.ACTION_SPLIT_HORIZONTAL:
            print("--- [ | ] change_container: 'split horizontal' on '%s'"%container.name)

            new_container = HSplitContainer(name = container.name + "_hsplit",
                                window = container.window,
                                batch = container.batch,
                                create_default_children = True)

            if container.parent is None:
                container.set_child( new_container, 0 )
            else:
                container = container.replace_by( new_container )

            root = container.get_root_container()
            root.update()
            root.pprint_tree()


        case Container.ACTION_SPLIT_VERTICAL:
            print("--- [---] change_container: 'split vertical' on '%s'"%container.name)

            new_container = VSplitContainer(name = container.name + "_vsplit",
                                window = container.window,
                                batch = container.batch,
                                create_default_children = True)
            
            if container.parent is None:
                container.set_child( new_container, 0 )
            else:
                container = container.replace_by( new_container )

            root = container.get_root_container()
            root.update()
            root.pprint_tree()


        case Container.ACTION_CLOSE:
            print("--- [ x ] change_container: 'close' on '%s'"%container.name)
            # TODO: ACTION_CLOSE #4
            if container.parent is None:
                raise RuntimeWarning("closing a root container is not allowed yet")
            parent : Container = container.parent
            if isinstance(parent, SplitContainer):

                # get sibling
                sibling = None
                if parent.children[0] is not container:
                    sibling = parent.children[0]
                elif parent.children[1] is not container:
                    sibling = parent.children[1]

                parent.remove_child( container )

                if sibling:
                    # get the grandparent
                    grandparent : Container = parent.parent
                    # remove the parent (SplitContainer)
                    idx = grandparent.remove_child( parent )
                    # add the sibling as the new child of grandparent
                    grandparent.set_child( sibling, idx )


            root = sibling.get_root_container()
            root.update()
            root.pprint_tree()


        case Container.ACTION_CLOSE_SPLIT:
            print("--- [<-x] change_container: 'close split' on '%s'"%container.name)
            # close a sibling if parent is a split container
            # (I think it nearly always is, if using the menu to change containers)


        case Container.ACTION_CLOSE_OTHERS:
            print("--- [xxO] change_container: 'close others' on '%s'"%container.name)
            # Stash this container.
            # Find root.
            # Remove children of root.
            # Add stashed this-container to the root.
            root = container.get_root_container()

            idx = container.parent.children.index( container )
            container.parent.children[idx] = None

            root.remove_children()
            root.set_child( container, 0 )
            root.update()
            root.pprint_tree()


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    print("run containers.py main:")

    import sys
    from imgui.integrations.pyglet import create_renderer
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

    win = pyglet.window.Window( width=960, height=540, config=_window_config, resizable=True )
    
    fps_display = pyglet.window.FPSDisplay(win)
    fps_display.update_period = 0.2

    line_batch = pyglet.graphics.Batch()


    # test container events: ---------------------------------------------------
    def mouse_entered_container( container ) -> None:
        """test"""
        print("--> mouse entered %s"%container.name)

    def mouse_exited_container( container ) -> None:
        """test"""
        print("o-- mouse exited %s"%container.name)


    # imgui --------------------------------------------------------------------
    imgui.create_context()
    imgui_renderer = create_renderer(win)
    imgui_io = imgui.get_io()
    font_default = imgui_io.fonts.add_font_from_file_ttf("boxer/resources/fonts/DejaVuSansCondensed.ttf", 14 )
    font_default_bold = imgui_io.fonts.add_font_from_file_ttf("boxer/resources/fonts/DejaVuSansCondensed-Bold.ttf", 14 )
    font_small = imgui_io.fonts.add_font_from_file_ttf("boxer/resources/fonts/DejaVuSansCondensed.ttf", 10 )
    font_t1 = imgui_io.fonts.add_font_from_file_ttf("boxer/resources/fonts/DejaVuSansCondensed.ttf", 23 )
    imgui_renderer.refresh_font_texture()


    # container tree -----------------------------------------------------------
    # c = HSplitContainer(name="root_container", ratio=0.36, window = win, batch = line_batch)
    # c = HSplitContainer(name="root_container",
    #                     ratio=0.36,
    #                     window = win,
    #                     batch = line_batch,
    #                     position=pyglet.math.Vec2(50,50),
    #                     width= 615,
    #                     height=320,
    #                     use_explicit_dimensions=True)
    c = Container(name="root_container",
                        window = win,
                        batch = line_batch,
                        position=pyglet.math.Vec2(50,50),
                        width= 615,
                        height=320,
                        use_explicit_dimensions=True)

    # # c.push_handlers( mouse_entered = mouse_entered_container )
    # # c.push_handlers( mouse_exited = mouse_exited_container )

    # # ---
    # c_l = Container(name = "left_panel", batch = line_batch)
    # # c_l.push_handlers( mouse_entered = mouse_entered_container )
    # # c_l.push_handlers( mouse_exited = mouse_exited_container )
    # c.add_child( c_l )

    # c_r = VSplitContainer(name= "right_panel", batch = line_batch, ratio = 0.333,color=(128,128,255,0))
    # # c_r.push_handlers( mouse_entered = mouse_entered_container )
    # # c_r.push_handlers( mouse_exited = mouse_exited_container )
    # c.add_child( c_r )

    # c_r_one = Container(name="right_panel_bottom", batch = line_batch, color=(128, 255, 128, 128))
    # # c_r_one.push_handlers( mouse_entered = mouse_entered_container )
    # # c_r_one.push_handlers( mouse_exited = mouse_exited_container )
    # c_r.add_child( c_r_one )

    # c_fh = HSplitContainer(name="top_final_split", batch = line_batch, ratio = 0.65, color=(128,128,255,0))
    # # c_fh.push_handlers( mouse_entered = mouse_entered_container )
    # # c_fh.push_handlers( mouse_exited = mouse_exited_container )
    # c_r.add_child( c_fh )

    # cfh_left = VSplitContainer(name="final_split_left", batch=line_batch, color=(128,128,255,0))#, color=(255, 180, 10, 128))
    # # cfh_left.push_handlers( mouse_entered = mouse_entered_container )
    # # cfh_left.push_handlers( mouse_exited = mouse_exited_container )
    # c_fh.add_child( cfh_left )

    # cfh_left_bottom = Container(name ="final_split_left_bottom", batch=line_batch, color=(255, 180, 10, 128))
    # # cfh_left_bottom.push_handlers( mouse_entered = mouse_entered_container )
    # # cfh_left_bottom.push_handlers( mouse_exited = mouse_exited_container )
    # cfh_left.add_child(cfh_left_bottom)

    # cfh_left_top = Container(name ="final_split_left_top", batch=line_batch, color=(255, 180, 10, 128))
    # # cfh_left_top.push_handlers( mouse_entered = mouse_entered_container )
    # # cfh_left_top.push_handlers( mouse_exited = mouse_exited_container )
    # cfh_left.add_child(cfh_left_top)

    # cfh_right_vp = ViewportContainer(name="final_viewport", batch=line_batch, color=(255,255,255,128))
    # # cfh_right_vp.push_handlers( mouse_entered = mouse_entered_container )
    # # cfh_right_vp.push_handlers( mouse_exited = mouse_exited_container )
    # c_fh.add_child( cfh_right_vp )
    # # ---


    t1_start = perf_counter()
    # count, leaves = c.update_structure()
    # c.update_geometries()#count = 0)
    c.update()
    t1_stop = perf_counter()

    c.pprint_tree()

    print("leaves:")
    for leaf in c.leaves:
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
        # print("on_resize (%s, %s)"%(width, height))
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


        imgui.new_frame()
        # imgui.begin("Container imgui")
        imgui.push_font(font_default)
        line_batch.draw()


        for l in c.leaves:
            l.draw()

        imgui.pop_font()

        imgui.push_font(font_default)
        draw_container_tree_info( c )
        imgui.pop_font()

        imgui.end_frame()

        imgui.render()
        imgui_renderer.render(imgui.get_draw_data())

        fps_display.draw()

    app.run()
