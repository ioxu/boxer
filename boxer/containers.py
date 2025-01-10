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
import pyglet.math
from pyglet.window import Window # Pylance is getting confused
import boxer.camera
import boxer.shapes
import boxer.shaders
import boxer.handles
import boxer.mouse

import imgui as imgui

from typing import Optional
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

    CONTAINER_DEBUG_LABEL = False

    cog_image = pyglet.image.load("boxer/resources/cog_16.png")
    window_image = pyglet.image.load("boxer/resources/window_16.png")
    downarrow_image = pyglet.image.load("boxer/resources/downarrow_16.png")
    diamond_image = pyglet.image.load("boxer/resources/diamond_16.png")
    textures = {
        "cog" : cog_image.get_texture(),
        "window" : window_image.get_texture(),
        "downarrow" : downarrow_image.get_texture(),
        "view-combo" : diamond_image.get_texture(),
    }

    # container_view_types = ["none",
    #                     "graph",
    #                     "3d",
    #                     "parameters",
    #                     "spreadsheet",
    #                     "python",
    #                     "log",
    #                     "container debug"]
    container_view_types = [["none", None],
                        ]

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
            window = None,
            width : int = 128,
            height : int = 128,
            use_explicit_dimensions : bool = False,
            position : pyglet.math.Vec2 = pyglet.math.Vec2(0,0),
            color = (255, 255, 255, 60),
            batch = None,
            group = None,
            overlay_batch = None
            ):

        self.name = name
        self.window : Window = window or pyglet.window.Window()
        self.width = width
        self.height = height
        self.position : pyglet.math.Vec2 = position
        self.use_explicit_dimensions = use_explicit_dimensions 
        self.color = color
        self.batch : pyglet.graphics.Batch = batch or pyglet.graphics.Batch()
        self.overlay_batch : pyglet.graphics.Batch = overlay_batch or  pyglet.graphics.Batch()
        self.group : pyglet.graphics.Group = group or pyglet.graphics.Group()

        self.children = []
        self.parent = None

        # usually just the root container would hold an updated list of leaves.
        # container.update() sets this on whatever container update() is called on.
        # usually update a tree with container.get_root_container().update()
        self.leaves = []

        self.split_containers = []

        self.is_leaf = False
        self.is_root = False

        self.root_container : Container = self # either None or a Container

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

        # self.lines["top_bar"] = pyglet.shapes.Line( 0, 0, 1, 0,
        #                                     batch = self.batch,
        #                                     color = self.color )

        self._lines_original_color = self.color

        if self.CONTAINER_DEBUG_LABEL:
            self.debug_label_name = pyglet.text.Label(self.name,
                            font_size=8,
                            x=0, y=0,
                            anchor_x='left', anchor_y='top',
                            batch=batch,
                            color=( 255, 255, 255, 50),
                            width = 100,
                            multiline=True,)


        self.do_draw_overlay = False
        self._marchinglines_time = 0.0
        #self._marchinglines_shader = pyglet.shapes.get_default_shader()
        self._marchinglines_shader = boxer.shaders.get_marchinglines_shader()
        
        self._marchinglines_shader["color_one"] = (1.0, 0.1, 0.0, 0.25)
        #self._marchinglines_shader["line_ratio"] = 0.5
        self._marchinglines_shader["time"] = 0.0
        self._marchinglines_shader["ir_bl"] = (70.0, 70.0)    # inner rect, bottom left
        self._marchinglines_shader["ir_tr"] = (120.0, 120.0)    # inner rect, top right
        self._marchinglines_shader["positive"] = 1.0        # value of inner rect (1.0
                                                            # means black outside, 0.0 means black inside)

        _points = boxer.shapes.rectangle_centered_vertices( 130, 230, 200, 200 )
        _colors = (1.0, 1.0, 1.0, 1.0) * 4
        self.overlay_quad = self._marchinglines_shader.vertex_list_indexed( 4,
                                        gl.GL_TRIANGLES,
                                        (0,1,2,0,2,3),
                                        self.overlay_batch,
                                        None,
                                        position = ('f', _points),
                                        colors = ('f', _colors),
                                        )

        # imgui
        self.container_view_combo_selected = 0
        self.container_actions_combo_selected = 0


    def __del__(self) -> None:
        # print("\033[31m[X]\033[0m '%s' being deleted."%self.name)
        print("\033[38;5;52m[X]\033[0m '%s' being deleted."%self.name)


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

        old_children = old_children + self.children 
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
                old_children = child.remove_children( old_children )
  
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


    def get_child_size(self, this) -> pyglet.math.Vec2:
        """calculate the width and height available for a child
        ('this' is normally self!)
        subclasses should override this method for their own caclulations
        """
        return pyglet.math.Vec2(self.width, self.height)


    def get_available_size_from_parent( self ) -> tuple:
        """ask parent for available size"""
        if self.use_explicit_dimensions:
            # do not modify size
            return (self.width, self.height)
        if hasattr(self.parent, "get_child_size"):
            # likely a Container 
            ps = self.parent.get_child_size( self ) # type: ignore
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


    def get_position_from_parent( self ) -> pyglet.math.Vec2:#-> tuple:
        """ask this node's parent of a position to place self"""
        if self.use_explicit_dimensions:
            # do not modify position
            return self.position
        if hasattr(self.parent, "get_child_position"):
            # likely a Container
            assert self.parent is not None
            self.position = self.parent.get_child_position( self )
            return self.position
        if self.parent is None:
            # maybe its a pyglet.window.Window ?
            if self.window and not self.use_explicit_dimensions:
                self.position = pyglet.math.Vec2(0,0)
            return self.position
        # return (None, None)
        return pyglet.math.Vec2(0,0)


    @ property
    def child_count(self):
        """return the number of children"""
        return len(self.children)


    def pprint_tree(self, depth : int = 0) -> None:
        """prety prints the structure, indented by depth"""
        if depth == 0:
            print("-----------------------------------")
            print("Container %s tree pprint:"%(self,))
        
        self._depth = depth
        print("    "*depth, "%s (id: %s )"%(depth, self._node_id), "'%s'"%self.name, type(self).__name__ )#, "window: %s"%self.window)
        print("    "*depth, "  > size:", self.get_available_size_from_parent(), "position:", self.get_position_from_parent() )
        for child in self.children:
            child.pprint_tree( depth+1 )


    def update_geometries( self ) -> None:
        """traverse all children and update all geometries, positions, etc"""
        # print("\033[38;5;215mContainer update_geometries\033[0m (%s)"%self.name)
        self.get_available_size_from_parent()
        self.get_position_from_parent()

        margin = 1#3


        if self.is_root:
            self.overlay_quad.position = (self.position.x, self.position.y + self.height, 0.0, # type: ignore
                                            self.position.x + self.width, self.position.y + self.height, 0.0,
                                            self.position.x + self.width, self.position.y, 0.0,
                                            self.position.x, self.position.y, 0.0)

        if self.CONTAINER_DEBUG_LABEL:
            self.debug_label_name.x = self.position.x + 5
            self.debug_label_name.y = self.position.y + self.height - 2 - 15
            if self.is_leaf:
                self.debug_label_name.opacity = 100#0#50
            else:
                self.debug_label_name.opacity = 0

        self.lines["left"].x = self.position.x + margin
        self.lines["left"].y = self.position.y + margin
        self.lines["left"].x2 = self.position.x + margin
        self.lines["left"].y2 = self.position.y + self.height - margin

        self.lines["top"].x = self.position.x + margin #-1
        self.lines["top"].y = self.position.y + self.height - margin
        self.lines["top"].x2 = self.position.x + self.width - margin
        self.lines["top"].y2 = self.position.y + self.height - margin

        self.lines["right"].x = self.position.x + self.width - margin
        self.lines["right"].y = self.position.y + self.height - margin
        self.lines["right"].x2 = self.position.x + self.width - margin
        self.lines["right"].y2 = self.position.y + margin #+ 1

        self.lines["bottom"].x = self.position.x + margin
        self.lines["bottom"].y = self.position.y + margin
        self.lines["bottom"].x2 = self.position.x + self.width -margin
        self.lines["bottom"].y2 = self.position.y + margin


        # self.lines["top_bar"].x = self.position.x + margin #-1
        # self.lines["top_bar"].y = self.position.y + self.height - margin - 18.0
        # self.lines["top_bar"].x2 = self.position.x + self.width - margin
        # self.lines["top_bar"].y2 = self.position.y + self.height - margin - 18.0

        self.update_display()

        if self.is_leaf:
            self.root_container.dispatch_event("resized", self)

        for child in [c for c in self.children if c is not None]:
            child.update_geometries()


    def update_display( self, ) -> None:
        """update graphical display/feedback things
        labels, inside/outside line colours/opacities etc
        """
        if self.CONTAINER_DEBUG_LABEL:
            if self.is_leaf:
                self.debug_label_name.text =\
                    self.name + " (%s)"%(type(self).__name__) +\
                    "\n.is_leaf " +\
                    str(self.is_leaf) +\
                    "\n.mouse_inside " +\
                    str(self.mouse_inside)

        if self.mouse_inside:
            for lk in self.lines.items():
                lk[1].width = 0.5#1.5
                lk[1].opacity = self._lines_original_color[3] + 65 #255
        else:
            if self.is_leaf:
                for lk in self.lines.items():
                    lk[1].width = .5
                    lk[1].opacity = self._lines_original_color[3]
            else:
                for lk in self.lines.items():
                    lk[1].opacity = 0        


    # def update_structure( self, depth : int = 0, count : int = 0, leaves = None, root = None ) -> tuple[int, list, 'Container']:
    def update_structure( self, depth : int = 0, count : int = 0, leaves = None, root = None ) -> tuple[int, list, 'Container']:
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

        if depth == 0:
            self.is_root = True
            root = self
            self.root_container = self
            self.root_container.split_containers = []
        else:
            assert root is not None
            self.root_container = root

        # ----------------------------------------------------------------------
        if isinstance(self, SplitContainer):
            #print("IS INSTANCE %s %s"%(self, SplitContainer))
            self.root_container.split_containers.append( self )

        # ----------------------------------------------------------------------
        # remove all handlers first?
        # TODO: how to parameterise functions to pop handlers from #3 @ioxu
        # Container handlers:
        #[{'mouse_exited': <function mouse_exited_container at 0x000001EBEFF709D0>},
        #{'mouse_entered': <function mouse_entered_container at 0x000001EBEFF70700>},
        #{'resized': <function on_container_resized at 0x000001EBEFF70C10>},
        #{'collapsed': <function on_container_collapsed at 0x000001EBEFF70B80>},
        #{'split': <function on_container_split at 0x000001EBEFF70AF0>},
        #{'view_changed': <function on_container_view_changed at 0x000001EBEFF70A60>}]
        if self.window:
            self.window.remove_handlers(on_mouse_motion=self.on_mouse_motion)
            
            # # loop events on object
            # for d in self._event_stack:
                
            #     # get the single key in the dict, check if in list of events
            #     if list(d)[0] in ["mouse_entered", "mouse_exited"]:
            #         # remove event
            #         print("\033[38;5;45mremoving %s event from %s\033[0m"%( d, self ))
            #         self.remove_handlers( d )

            # self.remove_handlers( mouse_entered = mouse_entered_container )
            # self.remove_handlers( mouse_exited = mouse_exited_container )
        # ----------------------------------------------------------------------

        if len(self.children) == 0:
            self.is_leaf = True
            leaves.append( self )
            # add handers for leaves -------------------------------------------
            # TODO: how to parameterise functions to push handlers to #3 @ioxu
            if self.window:
                self.window.push_handlers(on_mouse_motion=self.on_mouse_motion)
                # self.push_handlers( mouse_entered = mouse_entered_container )
                # self.push_handlers( mouse_exited = mouse_exited_container )
            # ------------------------------------------------------------------
        else:
            self.is_leaf = False
            self.mouse_inside = False
            if self in leaves:
                leaves.remove(self)

            for child in self.children:
                count, leaves, root = child.update_structure( depth+1, count, leaves, root )
        return count, leaves, root


    def update(self) -> None:
        """update both geometries and structure
        
        calls
        self.update_structure()
        self.update_geometries()
        """

        _, self.leaves, _ = self.update_structure()
        self.update_geometries()

        # TODO: make update() support updating the downstream child-tree of THIS node.
        # if self._node_id == None:
        #     self._node_id = 0

        # _, self.root_container.leaves, _ = self.update_structure(
        #                             depth = self._depth,
        #                             count = self._node_id,
        #                             leaves = self.root_container.leaves,
        #                             root = self.root_container)
        # self.update_geometries()


    def draw_leaf(self):
        """draw self as a leaf (only draws as a single leaf container)"""
        # maybe just draw a coloured outline
        # NO DRAW, ONLY BATCH.


        #----------------------------------------------------------------------
        # FIXME: Container.leaves can be modified during the loop!!
        # because imgui is immediate mode, activating callbacks from imgui ui
        # call updates to the container heirarchy which recalculates the tree's
        # leaves. This is such a bad pattern by me.
        if self.window is None:
            print("\033[38;5;196mdraw_leaf: %s .window is None\033[0m"%self)
            return
        #----------------------------------------------------------------------

        pos = self.position

        # imgui ----------------------------------------------------------------
        # no decoration / no collapsible title bar
        container_imwindow_flags = imgui.WINDOW_NO_TITLE_BAR\
                            | imgui.WINDOW_NO_BACKGROUND\
                            | imgui.WINDOW_NO_RESIZE\
                            | imgui.WINDOW_NO_SAVED_SETTINGS\
                            | imgui.WINDOW_NO_SCROLLBAR\
                            | imgui.WINDOW_NO_BRING_TO_FRONT_ON_FOCUS

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

        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING , imgui.Vec2(3.0, 3.0)) # type: ignore

        imgui.push_style_var(imgui.STYLE_FRAME_ROUNDING, 2.0)
        imgui.push_style_var(imgui.STYLE_ITEM_SPACING, imgui.Vec2(-1.0, 0.0)) # type: ignore
        imgui.push_style_color(imgui.COLOR_BUTTON, 0.0, 0.0, 0.0, 0.0)
        imgui.push_style_color(imgui.COLOR_BUTTON_ACTIVE, 1.0, 1.0, 1.0, 0.3)
        imgui.push_style_color(imgui.COLOR_BUTTON_HOVERED, 1.0, 1.0, 1.0, 0.2)
        
        with imgui.begin(self.name, flags = container_imwindow_flags ) as imgui_window:
            imgui.push_clip_rect(\
                            pos[0],
                            self.window.height - pos[1] - self.height,
                            pos[0] + self.width -1,
                            self.window.height - pos[1] - 1)
            imgui.push_style_var(imgui.STYLE_FRAME_PADDING, imgui.Vec2(1.0, 1.0)) # type: ignore
            imgui.push_style_var(imgui.STYLE_ITEM_SPACING, imgui.Vec2(0.0, 0.0)) # type: ignore
            imgui.image_button( self.textures["cog"].id, 12, 12)
            imgui.same_line()

            
            imgui.push_item_width(80)

            # viewtype combo ---------------------------------------------------
            imgui.image_button( self.textures["view-combo"].id, 12, 12, uv0=(0.0, 1.0), uv1=(1.0, 0.0) )
            if imgui.is_item_clicked( 0 ):
                curr_cursor_pos = imgui.get_cursor_screen_position()  # type: ignore
                popup_pos = imgui.Vec2( curr_cursor_pos.x+12, curr_cursor_pos.y ) # type: ignore
                imgui.set_next_window_position( popup_pos.x, popup_pos.y )
                imgui.open_popup( "container-view-type" )

            imgui.same_line() 
            with imgui.begin_popup( "container-view-type" ) as container_view_popup:
                imgui.push_style_var(imgui.STYLE_ITEM_SPACING, imgui.Vec2(3.0, 3.0))
                if container_view_popup.opened:
                    imgui.text("view type")
                    imgui.separator()

                    for container_view_index, container_view_item in enumerate( Container.container_view_types ):
                        if container_view_index ==1:
                            imgui.separator()
                        is_view_selected = (container_view_index == self.container_view_combo_selected)
                        
                        imgui.selectable( container_view_item[0], is_view_selected )
                        if imgui.is_mouse_released(0) and imgui.is_item_hovered():
                            self.container_view_combo_selected = container_view_index
                            
                            if not is_view_selected:
                                self.get_root_container().dispatch_event( "view_changed", self, container_view_item )

                            imgui.close_current_popup()
                        
                        if is_view_selected:
                            imgui.set_item_default_focus()

                        
                imgui.pop_style_var(1)


            # ------------------------------------------------------------------
            imgui.pop_item_width()

            imgui.same_line()
            #imgui.text(self.name)

            # container action combo -------------------------------------------

            do_container_action = False
            action_item_hovered = None
            do_draw_container_action_hint = False


            imgui.set_cursor_pos( (self.width - (15+3.0) , 3.0) )

            imgui.image_button( self.textures["downarrow"].id, 12, 12, uv0=(0,1), uv1=(1,0) )
            if imgui.is_item_clicked( 0 ):
                popup_pos = imgui.Vec2( self.position.x + self.width - (15+3.0) , self.window.height - self.position.y - self.height +19)
                imgui.set_next_window_position( popup_pos.x, popup_pos.y )
                imgui.open_popup("container-actions")

            imgui.same_line()
            with imgui.begin_popup("container-actions") as select_popup:
                imgui.push_style_var(imgui.STYLE_ITEM_SPACING, imgui.Vec2(3.0, 3.0))
                if select_popup.opened:
                    imgui.text("container-actions")
                    imgui.separator()
    
                    for action_index, action_item in enumerate( Container.container_action_labels):

                        if action_index == 2:
                            imgui.separator()

                        # if imgui.selectable( action_item, selected = False )[0]:
                        _, selected = imgui.selectable( action_item, selected = False )

                        if imgui.is_mouse_released(0) and imgui.is_item_hovered():
                            self.container_actions_combo_selected = action_index
                            print("container action: '%s' (%s)"%(\
                                    Container.container_action_labels[self.container_actions_combo_selected],
                                    self.name)
                            )
                            do_container_action = True
                            imgui.close_current_popup()

                        if imgui.is_item_hovered():
                            action_item_hovered = action_index
                            do_draw_container_action_hint = True
                        else:
                            self.root_container.do_draw_overlay = False

                imgui.pop_style_var(1)

            


            imgui.pop_style_var(2)
            imgui.pop_clip_rect()
        
        imgui.pop_style_color(3) # button colors
        imgui.pop_style_var(1) # item spacing
        imgui.pop_style_var(1) # rounded buttons
        
        imgui.pop_style_var()


        split_line_hint_width = 15.0

        if do_draw_container_action_hint:
            match action_item_hovered:
                case Container.ACTION_SPLIT_HORIZONTAL:
                    self.root_container.do_draw_overlay = True
                    bl = self.position + pyglet.math.Vec2((self.width / 2.0) - (split_line_hint_width/2.0), 0.0)
                    tr = ( bl[0] + split_line_hint_width, bl[1] + self.height )
                    self.root_container._marchinglines_shader["ir_bl"] = bl
                    self.root_container._marchinglines_shader["ir_tr"] = tr
                    self.root_container._marchinglines_shader["positive"] = 1.0

                case Container.ACTION_SPLIT_VERTICAL:
                    self.root_container.do_draw_overlay = True
                    bl = self.position + pyglet.math.Vec2( 0.0, (self.height/2.0) - (split_line_hint_width / 2.0 ) )
                    tr = ( bl[0] + self.width, bl[1] + split_line_hint_width )
                    self.root_container._marchinglines_shader["ir_bl"] = bl
                    self.root_container._marchinglines_shader["ir_tr"] = tr
                    self.root_container._marchinglines_shader["positive"] = 1.0               

                case Container.ACTION_CLOSE:
                    self.root_container.do_draw_overlay = True
                    bl = self.position
                    tr = ( bl[0] + self.width, bl[1] + self.height )
                    self.root_container._marchinglines_shader["ir_bl"] = bl
                    self.root_container._marchinglines_shader["ir_tr"] = tr
                    self.root_container._marchinglines_shader["positive"] = 1.0

                case Container.ACTION_CLOSE_SPLIT:
                    # get sibling
                    sibling = None
                    if self.parent and isinstance(self.parent, SplitContainer):
                        self.root_container.do_draw_overlay = True
                        if self.parent.children[0] is not self:
                            sibling = self.parent.children[0]
                        elif self.parent.children[1] is not self:
                            sibling = self.parent.children[1]

                        bl = sibling.position
                        tr = ( bl[0] + sibling.width, bl[1] + sibling.height )
                        self.root_container._marchinglines_shader["ir_bl"] = bl
                        self.root_container._marchinglines_shader["ir_tr"] = tr
                        self.root_container._marchinglines_shader["positive"] = 1.0

                case Container.ACTION_CLOSE_OTHERS:
                    self.root_container.do_draw_overlay = True
                    bl = self.position
                    tr = ( bl[0] + self.width, bl[1] + self.height )
                    self.root_container._marchinglines_shader["ir_bl"] = bl
                    self.root_container._marchinglines_shader["ir_tr"] = tr                   
                    self.root_container._marchinglines_shader["positive"] = 0.0


                case _:
                    self.root_container.do_draw_overlay = False


        if do_container_action:
            self.root_container.do_draw_overlay = False
            change_container( self, self.container_actions_combo_selected )


    def draw(self) -> None:
        """root container draw method"""
  
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        self.batch.draw()
        
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        self.draw_overlay()


        
        # draw things for all SplitContainers
        # right-click context menu for splitters etc
        for h in self.split_containers:
            h.draw_handle_ui()

        # draw leaf containers, mostly imgui ui
        for l in self.leaves:
            l.draw_leaf()
 

    def draw_overlay(self) -> None:
        if self.root_container.do_draw_overlay:
            self._marchinglines_time += 1.5
            self._marchinglines_shader["time"] = self._marchinglines_time
            self.overlay_batch.draw()


    def on_mouse_motion(self, x, y, ds, dy) -> None:
        """to be bound to a pyglet.window.Window's mouse events"""
        _prev_mouse_inside = self.mouse_inside
        if boxer.shapes.point_in_box( x, y,
                self.position.x,
                self.position.y,
                self.position.x+self.width,
                self.position.y+self.height ):
            self.mouse_inside = True
            if _prev_mouse_inside is not True:
                self.update_display()
                # ret = self.dispatch_event( "mouse_entered", self )
                ret = self.root_container.dispatch_event( "mouse_entered", self )
                # print("dispatch event 'mouse_entered' for %s: return: %s"%(self.name, ret))
        else:
            self.mouse_inside = False
            if _prev_mouse_inside is True:
                self.update_display()
                # ret = self.dispatch_event( "mouse_exited", self )
                ret = self.root_container.dispatch_event( "mouse_exited", self )
                # ret = self.dispatch_event( "mouse_exited", self )
                # print("dispatch event 'mouse_exited' for %s: return: %s"%(self.name, ret))


# ------------------------------------------------------------------------------
# Container events

# mouse entering container
Container.register_event_type("mouse_entered")

# mouse exiting container
Container.register_event_type("mouse_exited")

# a container view type changed (by menu or method)
# self.dispatch_event( "view_changed", container : Container, view : List(view_name, class) )
Container.register_event_type("view_changed")

# a container view type removed (by menu or method)
# self.dispatch_event( "view_removed", container : Container, view : List(view_name, class) )
Container.register_event_type("view_removed")

# self.dispatch_event( "split",
#   container : Container, # the container that was split
#   new_containers : List # a list of the new child containers )
Container.register_event_type("split")

# TODO: container size changed
Container.register_event_type("resized")

# self.dispatch_event( "collapsed",
#   container : Container, # the container that was collapsed)
Container.register_event_type("collapsed")
# ------------------------------------------------------------------------------


class SplitContainer( Container ):
    """container that mannages a split view of twohildren"""

    ratio_modes = ["ratio", "fixed 0", "fixed 1"]
    RATIO_MODE_RATIO = 0        # uses a proportional ratio (0.0 .. 1.0) that adapt to parent's geometry
    RATIO_MODE_FIXED_0 = 1        # uses a fixed measure in pixels toward the child[0] side
    RATIO_MODE_FIXED_1 = 2        # uses a fixed measure in pixels toward the child[1] side

    def __init__(self,
            ratio : float = 0.5,
            create_default_children : bool = False,
            **kwargs):
        Container.__init__( self, **kwargs )
        self.ratio = ratio
        self.ratio_margin = 15 # limit from hitting 0 or 1, in pixels

        self.ratio_mode = SplitContainer.RATIO_MODE_RATIO

        self.create_default_children = create_default_children
        if self.create_default_children:
            self._default_children()

        self.split_handle = boxer.handles.BoxHandle(\
                position = pyglet.math.Vec2( 0.0, 0.0 ),
                name = self.name + "_RatioHandle",
                display_width = 5.0,
                display_height = 5.0,
                hit_width = 15.0,
                hit_height = 15.0,
                mouse = None,#self.mouse,
                debug = False,
                space = boxer.handles.Handle.SPACE_WORLD,
                #batch = self.batch,
                )

        if self.window:
            self.window.push_handlers( on_mouse_motion = self.split_handle.on_mouse_motion )
            self.window.push_handlers( on_mouse_press = self.split_handle.on_mouse_press )
            self.window.push_handlers( on_mouse_release = self.split_handle.on_mouse_release )
            self.window.push_handlers( on_mouse_drag = self.split_handle.on_mouse_drag )

        self.split_handle.push_handlers( position_updated = self.on_split_handle_position_updated )
        self.split_handle.push_handlers( mouse_entered = self.on_split_handle_mouse_entered )
        self.split_handle.push_handlers( mouse_exited = self.on_split_handle_mouse_exited )
        self.split_handle.push_handlers( pressed = self.on_split_handle_mouse_pressed )

        self.do_draw_handle_ui = False
        self.draw_handle_ui_rightclick_data = {}

        self.ratio_line = pyglet.shapes.Line( 0.0, 0.0, 1.0, 1.0,
                                            width = 4.0,
                                            color=(255,255,255,180),
                                            batch=self.batch )

        self._ratio_line_original_color = self.ratio_line.color
        self.ratio_line.color = self._ratio_line_original_color[:3]+(0,)


    def _default_children( self ):
        """generates default children
        for SplitContainer (a half abstract class) this will generate two children
        This method should be overwritten in subclasses
        """
        c1 = Container(name = self.name + "_cone", batch=self.batch, window=self.window)
        c2 = Container(name = self.name + "_ctwo", batch=self.batch, window=self.window)
        self.set_child( c1, 0 )
        self.set_child( c2, 1 )


    def update_geometries(self, *args, **kwargs) -> None:
        # print("\033[38;5;216mSplitContainer update_geometries\033[0m (%s)"%self.name)
        super().update_geometries(*args, **kwargs)


    def on_split_handle_position_updated(self, position) -> None:
        # print("\033[38;5;123m%s.split_handle position:\033[0m %s"%(self.name, position))
        ...

    
    def on_split_handle_mouse_pressed(self, x, y, buttons, modifiers) -> None:
        """event handler for mouse press on SplitContainer mouse press
        """
        print("\033[38;5;93m-^- \033[38;5;237m[h]\033[38;5;245m on_split_handle_mouse_pressed %s \033[0m %s, %s, %s, %s"%(self.name, x, y, buttons, modifiers))
        if buttons & pyglet.window.mouse.RIGHT:
            # right-click control for SplitContainer splitter bars
            # this pattern is very annoying.
            # the right-click detection is done here, SplitContainers are collected in
            # Container.update_structure() and the SplitContainer.draw_handle_ui() is called 
            # in Container.draw()
            self.do_draw_handle_ui = True
            self.draw_handle_ui_rightclick_data = {"x": x, "y": self.window.height - y, "buttons": buttons, "modifiers": modifiers}


    def draw_handle_ui(self) -> None:
        """draws SplitContainer splitter bar interface, triggered on right-click
        """
        # see above for pattern
        if self.do_draw_handle_ui:
            popup_pos = imgui.Vec2( self.draw_handle_ui_rightclick_data["x"], self.draw_handle_ui_rightclick_data["y"] )
            imgui.set_next_window_position( popup_pos.x, popup_pos.y )
            imgui.open_popup( "split-container-right-click-context-menu" )
            with imgui.begin_popup( "split-container-right-click-context-menu" ) as split_handle_context_menu:
                #print("RIGHT CLICK 4 %s"%self.draw_handle_ui_rightclick_data)
                opened = [False, False, False]
                selected = [False, False, False]
                selected[self.ratio_mode] = True
                if split_handle_context_menu.opened:
                    opened[0], selected[0] = imgui.selectable("ratio", selected[0])
                    opened[1], selected[1] = imgui.selectable("fixed 0", selected[1])
                    opened[2], selected[2] = imgui.selectable("fixed 1", selected[2])

                    if True in opened:
                        # set menu selection
                        print("opened:selected", opened, selected)
                        self.ratio_mode = opened.index(True)
                        self.do_draw_handle_ui = False
                        imgui.close_current_popup()

                    if imgui.is_mouse_released(0):
                        # close on left-mouse-up
                        self.do_draw_handle_ui = False
                        imgui.close_current_popup()


    def on_split_handle_mouse_entered(self):
        print("\033[38;5;10m--> \033[38;5;237m[h]\033[38;5;245m on_split_handle_mouse_entered %s \033[0m"%self.name)
        self.ratio_line.color = self._ratio_line_original_color


    def on_split_handle_mouse_exited(self):
        print("\033[38;5;173mo-- \033[38;5;237m[h]\033[38;5;245m on_split_handle_mouse_exited %s \033[0m"%self.name)
        self.ratio_line.color = self._ratio_line_original_color[:3]+(0,)


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


    def get_child_size(self, this) -> pyglet.math.Vec2: #tuple:
        s0 = math.floor(self.width*self.ratio) -1.0
        if this == self.children[0]:
            # return pyglet.math.Vec2(math.floor(self.width*self.ratio) -1.0 , self.height  )
            return pyglet.math.Vec2( s0 , self.height  )
        else:
            # return pyglet.math.Vec2(math.ceil(self.width*(1-self.ratio)), self.height  )
            return pyglet.math.Vec2(self.width - s0 -1.0, self.height  )


    def get_child_position(self, this) -> pyglet.math.Vec2: # tuple:
        if this == self.children[0]:
            x = self.position.x
            y = self.position.y
        else:
            x = self.position.x + math.floor(self.width*self.ratio)
            y = self.position.y
        return pyglet.math.Vec2(x, y)


    def update_geometries(self, *args, **kwargs) -> None:
        # print("\033[38;5;217mHSplitContainer update_geometries\033[0m (%s)"%self.name)
        super().update_geometries(*args, **kwargs)

        if self.split_handle:
            self.split_handle.position = pyglet.math.Vec2(\
                                self.position.x + (self.width * self.ratio),
                                self.position.y + (self.height * 0.5 ))
            self.split_handle.hit_width = 10.0
            self.split_handle.hit_height = self.height - 20.0
            self.split_handle.display_width = 2.0
            self.split_handle.display_height = self.split_handle.hit_height - 2.0
            self.split_handle.set_shape_anchors()

            self.ratio_line.x = self.position.x + (self.width * self.ratio) -1.0
            self.ratio_line.y = self.position.y + 0.5 
            self.ratio_line.x2 = self.ratio_line.x
            self.ratio_line.y2 = self.ratio_line.y + self.height - 1.0

            self.split_handle.update_position(dispatch_event = False)


    def on_split_handle_position_updated(self, position) -> None:
        self.split_handle.position.y = self.position.x + int(self.height * 0.5 )
        x = min( self.position.x + self.width - self.ratio_margin, max( self.position.x + self.ratio_margin, self.split_handle.position.x ) )
        self.split_handle.position.x = x
        new_ratio = (x - self.position.x) / float(self.width)
        self.ratio = new_ratio
        self.update_geometries()


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


    def get_child_size(self, this) -> pyglet.math.Vec2:
        s0 = math.floor(self.height * self.ratio) -1.0
        
        if this == self.children[0]:
            # return pyglet.math.Vec2(self.width , math.floor(self.height * self.ratio) -1.0 )
            return pyglet.math.Vec2(self.width, s0)
        # return pyglet.math.Vec2(self.width , math.ceil(self.height * (1.0 - self.ratio))  )
        return pyglet.math.Vec2(self.width, self.height - s0 -1.0)


    def get_child_position(self, this) -> pyglet.math.Vec2:
        if this == self.children[0]:
            x = self.position.x
            y = self.position.y
        else:
            x = self.position.x
            y = self.position.y + math.floor(self.height*self.ratio)
        return pyglet.math.Vec2(x, y)


    def update_geometries(self, *args, **kwargs) -> None:
        # print("%s.update_geometries"%self.name)
        # print("\033[38;5;217mVSplitContainer update_geometries\033[0m (%s)"%self.name)
        super().update_geometries(*args, **kwargs)

        if self.split_handle:
            self.split_handle.position = pyglet.math.Vec2(\
                                self.position.x + (self.width * 0.5),
                                self.position.y + (self.height * self.ratio ))
            self.split_handle.hit_width = self.width - 20.0
            self.split_handle.hit_height = 10.0
            self.split_handle.display_width = self.split_handle.hit_width - 2.0
            self.split_handle.display_height = 2.0 
            self.split_handle.set_shape_anchors()

            self.ratio_line.x = self.position.x + 0.5
            self.ratio_line.y = self.position.y + (self.height * self.ratio) -1.0
            self.ratio_line.x2 = self.ratio_line.x + self.width - 1.0
            self.ratio_line.y2 = self.ratio_line.y

            self.split_handle.update_position(dispatch_event = False)


    def on_split_handle_position_updated(self, position) -> None:
        self.split_handle.position.x = self.position.x + int(self.width * 0.5 )
        y = min( self.position.y + self.height - self.ratio_margin, max( self.position.y + self.ratio_margin, self.split_handle.position.y ) )
        self.split_handle.position.y = y
        new_ratio = ( y - self.position.y) / float(self.height)
        self.ratio = new_ratio
        self.update_geometries()


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
                closable=True,
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

            original_container = container

            if container.parent is None:
                container.set_child( new_container, 0 )
            else:
                container = container.replace_by( new_container )

            root = container.get_root_container()
            root.update()
            root.pprint_tree()
            root.dispatch_event( "split", original_container, new_container.children.copy() )


        case Container.ACTION_SPLIT_VERTICAL:
            print("--- [---] change_container: 'split vertical' on '%s'"%container.name)

            new_container = VSplitContainer(name = container.name + "_vsplit",
                                window = container.window,
                                batch = container.batch,
                                create_default_children = True)
            
            original_container = container

            if container.parent is None:
                container.set_child( new_container, 0 )
            else:
                container = container.replace_by( new_container )

            root = container.get_root_container()
            root.update()
            root.pprint_tree()
            root.dispatch_event( "split", original_container, new_container.children.copy() )


        case Container.ACTION_CLOSE:
            print("--- [ x ] change_container: 'close' on '%s'"%container.name)
            # TODO: ACTION_CLOSE #4
            
            do_close = False
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

                do_close = True
                parent.remove_child( container )

                if sibling:
                    # get the grandparent
                    grandparent : Container = parent.parent
                    # remove the parent (SplitContainer)
                    idx = grandparent.remove_child( parent )
                    # add the sibling as the new child of grandparent
                    grandparent.set_child( sibling, idx )

            root = sibling.get_root_container()
            if do_close:
                root.dispatch_event( "collapsed", container )
            root.do_draw_overlay = False
            root.update()
            root.pprint_tree()


        case Container.ACTION_CLOSE_SPLIT:
            print("--- [<-x] change_container: 'close split' on '%s'"%container.name)
            # close a sibling if parent is a split container
            # (I think it nearly always is, if using the menu to change containers)
            root = container.get_root_container()
            root.do_draw_overlay = False
            if container.parent is None:
                raise RuntimeWarning("closing a root container is not allowed yet")
            
            parent : Container = container.parent

            # move this container out of the way of being neutralised
            idx = parent.children.index( container )
            parent.children[idx] = None

            # remove children of parent split container
            removed_children = parent.remove_children()
            
            for c in removed_children:
                if c and c.is_leaf:
                    root.dispatch_event("collapsed", c)

            # replace parent split container by this container
            parent.replace_by( container )
            root.update()
            root.pprint_tree()


        case Container.ACTION_CLOSE_OTHERS:
            print("--- [xxO] change_container: 'close others' on '%s'"%container.name)
            # Stash this container.
            # Find root.
            # Remove children of root.
            # Add stashed this-container to the root.
            root = container.get_root_container()
            root.do_draw_overlay = False

            # move this container out of the way of being neutralised
            idx = container.parent.children.index( container )
            container.parent.children[idx] = None

            removed_children = root.remove_children()
            
            # ONLY emit "collapsed" signal on leaf containers
            # TODO is this the right thing to do?
            for c in removed_children:
                if c and c.is_leaf:
                    #print("REMOVED CHILD: %s (is_leaf %s)"%(c, c.is_leaf))
                    root.dispatch_event("collapsed", c)

            root.set_child( container, 0 )
            root.update()
            root.pprint_tree()


# ------------------------------------------------------------------------------
# module main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    print("run containers.py main:")

    import sys
    from imgui.integrations.pyglet import create_renderer
    sys.path.extend("..")
    import pyglet.window
    from pyglet import app
    from pyglet.window import key
    from time import perf_counter

    Container.CONTAINER_DEBUG_LABEL = True

    _window_config = gl.Config(
        sample_buffers = 1,
        buffer_size = 32,
        samples = 16,
        depth_size = 16,
        double_buffer = True,
    )

    fullscreen = False

    win = pyglet.window.Window(\
                        width=960,
                        height=540,
                        resizable=True,
                        config=_window_config,
                        )
    
    fps_display = pyglet.window.FPSDisplay(win)
    fps_display.update_period = 0.2

    line_batch = pyglet.graphics.Batch()
    overlay_batch = pyglet.graphics.Batch()


    #---------------------------------------------------------------------------
    # container view types -----------------------------------------------------
    #---------------------------------------------------------------------------




    class ContainerView( pyglet.event.EventDispatcher ):
        ...

        def update_geometries( self, container : Container ) -> None:
            raise NotImplementedError


    class BlueView( ContainerView ):
        def __init__( self,
                color = (79, 110, 205, 128),
                batch : pyglet.graphics.Batch = None):
            _points = boxer.shapes.rectangle_centered_vertices( 130, 230, 200, 200 )
            _colors = (1.0, 1.0, 1.0, 1.0) * 4#color * 4
            
            self.batch = batch or pyglet.graphics.Batch()
            self._marchinglines_time = 0.0
            self._marchinglines_shader = boxer.shaders.get_marchinglines_shader()

            self._marchinglines_shader["color_one"] = (color[0]/255.0, color[1]/255.0, color[2]/255.0, color[3]/255.0)#(1.0, 0.1, 0.0, 0.25)
            self._marchinglines_shader["line_ratio"] = 0.1
            self._marchinglines_shader["line_width"] = 10
            self._marchinglines_shader["gap_alpha"] = 0.8
            self._marchinglines_shader["time"] = 0.0
            self._marchinglines_shader["ir_bl"] = (0.0, 0.0)    # inner rect, bottom left
            self._marchinglines_shader["ir_tr"] = (0.0, 0.0)    # inner rect, top right
            self._marchinglines_shader["positive"] = 0.0        # value of inner rect (1.0
                                                            # means black outside, 0.0 means black inside)

            self.vertex_list : pyglet.graphics.vertexdomain.VertexList = self._marchinglines_shader.vertex_list_indexed( 4,
                                            gl.GL_TRIANGLES,
                                            (0,1,2,0,2,3),
                                            self.batch,
                                            None,
                                            position = ('f', _points),
                                            colors = ('f', _colors),
                                            )

        def __del__(self) -> None:
            print("\033[38;5;52m[X]\033[0m '%s' being deleted."%self)
            self.vertex_list.delete()


        def update_geometries(self, container: Container) -> None:
            self._marchinglines_time -= 0.5
            self._marchinglines_shader["time"] = self._marchinglines_time
            self.vertex_list.position = ( container.position.x, container.position.y + container.height, 0.0,
                                        container.position.x + container.width, container.position.y + container.height, 0.0,
                                        container.position.x + container.width, container.position.y, 0.0,
                                        container.position.x, container.position.y, 0.0)


    # add a container view type to the class
    Container.container_view_types += [ ["blue view", BlueView], ]

    # set up container view batch
    container_view_batch = pyglet.graphics.Batch()

    # keep a dictionary of views 
    # { container_key = {view_type = view} }
    ########################################
    # this dict MUST be kept in sync after
    # container splits/collapses because references
    # here will stop released containers from being GC'd
    ########################################
    container_views = {}



    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------
    # test container events: ---------------------------------------------------
    def mouse_entered_container( container ) -> None:
        """test"""
        print("--> mouse entered %s"%container.name)


    def mouse_exited_container( container ) -> None:
        """test"""
        print("o-- mouse exited %s"%container.name)


    def on_container_view_changed( container : Container, view_type : list ) -> None:
        """callback to be connected to container view being changed
        controls instatiation of new views"""
        print('\033[38;5;63m[view type]\033[0m changed on \033[38;5;63m%s\033[0m to \033[38;5;153m"%s"\033[0m'%(container.name, view_type)  )
        


        # setting view to a None view
        if view_type[1] == None:
            #container_views[ container ] = None
            container_views.pop( container )

        # setting a view to the same kind of view
        # this can happen when:
        #   1) splitting a view which moves a view between containers which triggers the "view_changed" event
        elif container_views.get( container, None ):
            if isinstance(container_views[ container ], view_type[1] ):
                print(f"{container} is already a view {view_type[1]} ({container_views[ container ]}), NOT instancing a new view")
                return

        else:
            # instance the container view!
            print("instancing BlueView into batch: %s"%container_view_batch)
            view : ContainerView = view_type[1](
                batch = container_view_batch
            )
            print("instanciating %s "%view_type[1])
            print("instanciating object: %s "%view)
            container_views[ container ] = view
            view.update_geometries( container )

        print("container_views:")
        for k in container_views.keys():
            print("   %s: %s"%(k, container_views[k])  )


    def on_container_split( container: Container, new_children : list ):
        """callback to be connected to when containers are split"""
        print("on_container_split %s %s"%( container, str(new_children) ))
        print("  moving container view around to new child:")

        # check if container (original_contaier) is in the container_views dict
        if container in container_views.keys():
            print( "  container IS in container_views.keys()" )
            
            # then pop the container out of the container_views dict, which returns the view it had
            print("  popping the container %s out of 'container_views'"%container)
            this_view = container_views.pop( container, None)

            # then pop the container out of the container_views dict
            print( "  --> grabbed this view from the popped container: %s"%this_view )

            print("  putting first, new child container, and view back into 'container_views'")
            print("  first, new child container: %s"%new_children[0].name)
            this_container : Container = new_children[0]
            container_views[ this_container ] = this_view

            this_view.update_geometries( this_container )

            print( container_views )

            # set the view type on the new view-owner

            # find the type index of this_view, in Container.container_view_types
            type_index = None
            this_view_type = None
            for index, sublist in enumerate( Container.container_view_types ):
                #if sublist[1] == BlueView :
                this_view_type = sublist[1]
                if this_view_type:
                    if isinstance( this_view, this_view_type ):
                        type_index = index

            print("  type_index for %s is %s"%( this_view, type_index ) )

            # set the view type of this_container to the type index
            # TODO: need to make a Container method for setting the container view type,
            # because doing it here won't fire the view_changed event
            # BUT maybe that's not what we want, anyway.

            if type_index:
                this_container.container_view_combo_selected = type_index
                this_container.get_root_container().dispatch_event("view_changed", this_container, this_container.get_root_container().container_view_types[type_index])


    def on_container_collapsed( container : Container ):
        """callback to be hooked up when a container is closed"""        
        print("\033[38;5;196mon_container_collapsed:\033[0m %s"%container)
        
        container_views.pop( container, None )
        print(container_views)


    def on_container_resized( container : Container ):
        """callback to be connected to when container is resized"""
        #print("\033[38;5;111mon_container_resized:\033[0m %s"%container)
        if container in container_views.keys():
            container_views[container].update_geometries( container )


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
    c = Container(name="root_container",
                        window = win,
                        batch = line_batch,
                        overlay_batch=overlay_batch,
                        position=pyglet.math.Vec2(50,50),
                        width= 615,
                        height=320,
                        use_explicit_dimensions=False)

    c.push_handlers( view_changed = on_container_view_changed )
    c.push_handlers( split = on_container_split )
    c.push_handlers( collapsed = on_container_collapsed )
    c.push_handlers( resized = on_container_resized )

    c.push_handlers( mouse_entered = mouse_entered_container )
    c.push_handlers( mouse_exited = mouse_exited_container )

    # ---------------

    t1_start = perf_counter()
    c.update()
    print("Container handlers:")
    print("  %s"%str(c._event_stack))

    t1_stop = perf_counter()

    c.pprint_tree()

    print("leaves:")
    for leaf in c.leaves:
        print("    %s"%leaf.name)

    # ---------------
    print("time to 'update': %s"%( t1_stop - t1_start ))

    gtime = 0.0


    # ---------------
    @win.event
    def on_resize( width, height ):
        """resize"""
        print("main.on_resize (%s, %s)"%(width, height))
        c.update_geometries()


    @win.event
    def on_key_press(symbol, _modifiers):
        """key events"""
        if symbol == key.B:
            #####################################
            # make sure there is a breakpoint added
            # on the next 'print' line.
            #####################################
            print("break")

        # Alt-Enter: toggle fullscreen
        if symbol == key.ENTER:
            if _modifiers & key.MOD_ALT:
                toggle_fullscreen()


    def toggle_fullscreen() -> None:
        """toggles fullscreen window mode"""
        global fullscreen
        fullscreen = not fullscreen
        win.set_fullscreen( fullscreen )
    # ---------------


    @win.event
    def on_draw():

        pyglet.gl.glClearColor(0.1, 0.1, 0.1, 1)

        win.clear( )

        imgui.new_frame()
        # imgui.push_font(font_default)


        ########################################################################
        ########################################################################
        ########################################################################
        # move to container (root) method(s)

        # gl.glEnable(gl.GL_BLEND)
        # gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        # line_batch.draw()

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        container_view_batch.draw()
        
        # gl.glEnable(gl.GL_BLEND)
        # gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        # c.root_container.draw_overlay()

        # for l in c.leaves:
        #     l.draw_leaf()
        c.draw()
        ########################################################################
        ########################################################################
        ########################################################################

        # imgui.pop_font()

        # imgui.push_font(font_default)
        # draw_container_tree_info( c )

        # imgui.pop_font()
        # imgui.end_frame()

        imgui.render()
        imgui_renderer.render(imgui.get_draw_data())




        fps_display.draw()
    app.run()
