import pyglet
import boxer.containers
import boxer.background
import boxer.camera
import imgui
import pyglet.gl as gl
import random
import gc
import atexit
import weakref

#-------------
_ranodm_uris = ["root", "root/sub_one", "root/sub_long_two"]
#-------------

class CanvasGroup( pyglet.graphics.Group ):
    ...


class GraphView( boxer.containers.ContainerView ):
        string_name = "Graph"

        imgui.create_context()
        io = imgui.get_io()
        font_t1 = io.fonts.add_font_from_file_ttf("boxer/resources/fonts/DejaVuSansCondensed.ttf", 12 )


        
        # a dictinoary of `GraphCanvas`es
        # key: subgraph URI key
        # value: GraphCanvas
        canvases = {}

        # canvas_views = weakref.WeakValueDictionary()
        canvas_views : dict[ type["GraphCanvas"], weakref.WeakSet["GraphView"] ] = {}

        # the GraphCanvas pyglet.graphics.Group
        canvas_group = CanvasGroup()#pyglet.graphics.Group()

        # the GraphView batch
        batch = pyglet.graphics.Batch()

        # views (instances of cls)
        views = weakref.WeakSet()

        @classmethod
        def draw_class( cls ) -> None:
            ##############################################################################
            # ContainerView subclass (Class, not Instance) iterates through canvas_views
            # -- iter thru GraphViews
            # ---- update class canvas_group (scissor and camera)
            # ---- draw canvas
            ##############################################################################
            print(f"draw_class {cls}")
            for canvas_view in cls.canvas_views:
                print(f"  canvas_view: {canvas_view}")
                for graph_view in cls.canvas_views[canvas_view]:
                    print(f"    update canvas_group {cls.canvas_group}")
                    print(f"      draw {canvas_view}")
                    canvas_view.draw()


        @classmethod
        def get_canvas_from_uri( cls, uri : str, graph_view_instance ):
            """fetch a cached GraphCanvas from uri, or create a new one.
            """
            print(f'{cls}.get_canvas_from_uri("{uri}")')
            if uri in GraphView.canvases:
                GraphView.canvas_views.setdefault( GraphView.canvases[uri], weakref.WeakSet() ).add( graph_view_instance ) # type: ignore
                pass
            else:
                _new_gc = GraphCanvas()
                GraphView.canvases[uri] = _new_gc
                # GraphView.canvas_views[ GraphView.canvases[uri] ] = graph_view_instance
                GraphView.canvas_views.setdefault( _new_gc, weakref.WeakSet() ).add( graph_view_instance ) # type: ignore
            return GraphView.canvases[uri]


        @classmethod
        def on_exit( cls ):
            """cleanup on app exit
            (using atexit module)"""
            print(f"atexit on_exit {cls}")
            rems = []
            for k in cls.canvases.keys():
                rems.append(k)
            for rem in rems:
                cls.canvases.pop( rem )
            # for c in cls.canvases:
            #     cc = cls.canvases[c]
            #     print(f"deleting canvas {cc}")
            #     # cc.__del__()
            #     refs = gc.get_referrers( cc )
            #     for ref in refs:
            #         print(f"  {ref}")
            #     del(cc)


        # def __init__( self, batch, **kwargs ):
        # def __init__( self, batch = None, **kwargs ):
        def __init__( self, **kwargs ):
            print("instancing 'Graph' ContainerView")
            super().__init__(self, **kwargs)
            
            # self.uri = "root"
            self.uri = random.choice(_ranodm_uris)
            self.canvas = GraphView.get_canvas_from_uri( self.uri, self )
            print(f'{self}.canvas = {self.canvas}')

            #self.batch = batch or pyglet.graphics.Batch()
            
            # if not GraphView.batch:
            #     GraphView.batch = pyglet.graphics.Batch()

            self.entered = False

            self.camera = boxer.camera.Camera( )
            # self.camera_group = boxer.camera.CameraGroup( self.camera )
            # self.bg_group = boxer.background.BackgroundGroup( parent = self.camera_group )
            #-----------------------------------------------------------------------------
            # https://pyglet.readthedocs.io/en/latest/programming_guide/rendering.html#batched-rendering
            # self.background : boxer.background.Background = boxer.background.Background(batch=batch) #, parent_group = self.camera_group)
            #-----------------------------------------------------------------------------

            self.group = pyglet.graphics.Group(1)

            self.margin = 0
            # self.bg_rect = pyglet.shapes.Rectangle(
            #     50, 50, 200, 200,
            #     #40, 8,
            #     (210, 210, 210, 90),
            #     pyglet.gl.GL_SRC_ALPHA,
            #     pyglet.gl.GL_ONE_MINUS_SRC_ALPHA,
            #     batch
            # )
            self.circle = pyglet.shapes.Circle(
                 10,10,
                 10,32,
                 (30,255,30,165),
                pyglet.gl.GL_SRC_ALPHA,
                pyglet.gl.GL_ONE_MINUS_SRC_ALPHA,
                GraphView.batch,
                self.group
            )

            self.mouse_circle = pyglet.shapes.Circle(
                 10,10,
                 20,32,
                (255,255,255,10),
                pyglet.gl.GL_SRC_ALPHA,
                pyglet.gl.GL_ONE_MINUS_SRC_ALPHA,
                GraphView.batch,
                self.group
            )

            self.view_label = pyglet.text.Label(
                "graph",
                font_size = 15.0,
                color = (255,255,255, 40),
                x = 10, y = 20,
                batch=GraphView.batch
            )

            self.hash_label = pyglet.text.Label(
                "graph",
                font_size = 9.0,
                color = (255,255,255, 65),
                x = 10, y = 20,
                batch=GraphView.batch,
                group=self.group
            )

            GraphView.views.add(self)


        def draw_imgui(self) -> None:

            # ----------------------------------------------------------------------------
            # URI breadcrumbs imgui 
            imgui.push_style_var(imgui.STYLE_WINDOW_PADDING , imgui.Vec2(3.0, 3.0)) # type: ignore
            imgui.push_style_var(imgui.STYLE_FRAME_ROUNDING, 2.0)
            imgui.push_style_var(imgui.STYLE_ITEM_SPACING, imgui.Vec2(-2.0, 0.0)) # type: ignore
            imgui.push_style_color(imgui.COLOR_BUTTON, 1.0, 0.675, 0, 0.15) #0.0, 0.0, 0.0, 0.3)
            imgui.push_style_color(imgui.COLOR_BUTTON_ACTIVE, 1.0, 1.0, 1.0, 0.3)
            imgui.push_style_color(imgui.COLOR_BUTTON_HOVERED, 1.0, 1.0, 1.0, 0.2)
            imgui.push_font(self.font_t1)

            imgui.set_cursor_pos((35, 0)) # type: ignore
            if imgui.button("graph://"):
                self.graph_view_local_function()
            imgui.same_line()

            imgui.button( self.uri )
            imgui.same_line()
            imgui.text("/")
            
            imgui.pop_font() # _t1
            imgui.pop_style_color(3) # button colors
            imgui.pop_style_var(1) # item spacing
            imgui.pop_style_var(1) # rounded buttons            
            imgui.pop_style_var() # window padding


        def graph_view_local_function(self) -> None:
            print(f"CLICKED graph:// from {self} (and this is a method on the instance)")


        def __del__(self) -> None:
            print(f"deleting GraphView {self}")

            # self.bg_rect.delete()
            # print("------------")
            # print(gc.get_referrers( self.background ))
            # print("------------")
            # pyglet.clock.unschedule(self.background.on_update) # fush this is so tedious
            # del(self.background.group)
            # del(self.background)
            # self.batch.invalidate() # to update the change in Groups associated with the Batch
            self.circle.delete()
            self.mouse_circle.delete()
            self.view_label.delete()
            self.hash_label.delete()
            # self.disconnect_handlers()
            super().__del__()


        def update_geometries(self, container):
            super().update_geometries( container )

            m = self.margin
            self.circle.position = (container.position.x + container.width - 18.0, container.position.y + 18.0)

            # label
            self.view_label.position = pyglet.math.Vec3( container.position.x + 10, container.position.y + (self.view_label.content_height * 0.5) , 0 )
            self.hash_label.text = str(hash(self))
            self.hash_label.position = pyglet.math.Vec3( container.position.x + 10 + self.view_label.content_width + 10, container.position.y + (self.view_label.content_height * 0.5) , 0 )

            # self.background.set_scissor( self.position.x, self.position.y, self.width, self.height )


        def connect_handlers(self, target) -> None:
            self.entered = True
            self.mouse_circle.color = (*self.mouse_circle.color[:3], 10)
            target.push_handlers( on_mouse_motion=self.on_mouse_motion )


        def disconnect_handlers(self, target) -> None:
            self.entered = False
            self.mouse_circle.color = (*self.mouse_circle.color[:3], 0)
            target.remove_handlers( on_mouse_motion=self.on_mouse_motion )


        def on_mouse_motion( self, x, y, dx, dy ) -> None:
            # print(f"ParameterView.on_mouse_motion() {x} {y} {dx} {dy}")
            self.mouse_circle.position = pyglet.math.Vec2( x, y )


        def draw_instance(self ) -> None:
            ##############################################################################
            # CONVERT: [ContainerView] convert to class method draw
            # I want to convert this to a class method
            # the class method is holding class instances in .views
            # - ContainerView subclass (Class, not Instance) iterates through canvases (GraphView.canvases)
            # ---- iterate through views associate with canvas (GraphView.canvas_views[ canvas ])
            # -------- update class canvas_group (scissor and camera)
            # -------- draw canvas
            
            # or
            # ContainerView subclass (Class, not Instance) iterates through canvas_views
            # -- iter thru GraphViews
            # ---- update class canvas_group (scissor and camera)
            # ---- draw canvas
            ##############################################################################


            # set scissor here !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # I don't want to set the scissor every frame
            canvas = GraphView.canvases[self.uri]
            canvas.background.group.set_scissor( self.position.x, self.position.y, self.width, self.height )
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            canvas.draw()
            self.batch.draw()


atexit.register( GraphView.on_exit )


class GraphCanvas(  pyglet.event.EventDispatcher ):
    """
    Actual display and interactions for a network graph
    """
    def __init__(self, **kwargs):
        self.batch = pyglet.graphics.Batch()
        self.background : boxer.background.Background = boxer.background.Background(batch=self.batch, group=GraphView.canvas_group)


    def __del__(self) -> None:
        print(f"deleting GraphCanvas {self}")
        # print("8<-----------------------")
        # self.batch._dump_draw_list()
        # print("----------------------->8")
        pyglet.clock.unschedule(self.background.on_update)
        del(self.background)
        self.batch.invalidate()
        del(self.batch)


    def draw(self) -> None:
        self.batch.draw()
