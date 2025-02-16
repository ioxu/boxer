import pyglet
import boxer.containers
import boxer.background
import imgui
import pyglet.gl as gl
import random

class GraphView( boxer.containers.ContainerView ):
        string_name = "Graph"

        imgui.create_context()
        io = imgui.get_io()
        font_t1 = io.fonts.add_font_from_file_ttf("boxer/resources/fonts/DejaVuSansCondensed.ttf", 12 )

        _name_list = ["subgraph", "parts", "components"]



        def __init__( self, batch = None, **kwargs ):
            print("instancing 'Graph' ContainerView")
            super().__init__(self, **kwargs)
            
            self.batch = batch
            self.entered = False

            #-----------------------------------------------------------------------------
            # https://pyglet.readthedocs.io/en/latest/programming_guide/rendering.html#batched-rendering
            self.background : boxer.background.Background = boxer.background.Background(batch=batch)
            #-----------------------------------------------------------------------------

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
                 (30,255,30,200),
                pyglet.gl.GL_SRC_ALPHA,
                pyglet.gl.GL_ONE_MINUS_SRC_ALPHA,
                batch
            )

            self.mouse_circle = pyglet.shapes.Circle(
                 10,10,
                 20,32,
                (255,255,255,10),
                pyglet.gl.GL_SRC_ALPHA,
                pyglet.gl.GL_ONE_MINUS_SRC_ALPHA,
                batch
            )

            self.view_label = pyglet.text.Label(
                "graph",
                font_size = 15.0,
                color = (255,255,255, 40),
                x = 10, y = 20,
                batch=batch
            )

            self.hash_label = pyglet.text.Label(
                "graph",
                font_size = 9.0,
                color = (255,255,255, 65),
                x = 10, y = 20,
                batch=batch
            )

            # test to make unique paths to show in each GraphView's breadcrumb
            self._name_list_r = []
            for i in range(len(self._name_list)):
                self._name_list_r.append( random.choice( self._name_list ) )


        def draw_imgui(self) -> None:

            # ----------------------------------------------------------------------------
            # URI breadcrumbs imgui 
            imgui.push_style_var(imgui.STYLE_WINDOW_PADDING , imgui.Vec2(3.0, 3.0)) # type: ignore
            imgui.push_style_var(imgui.STYLE_FRAME_ROUNDING, 2.0)
            imgui.push_style_var(imgui.STYLE_ITEM_SPACING, imgui.Vec2(-2.0, 0.0)) # type: ignore
            imgui.push_style_color(imgui.COLOR_BUTTON, 0.0, 0.0, 0.0, 0.0)
            imgui.push_style_color(imgui.COLOR_BUTTON_ACTIVE, 1.0, 1.0, 1.0, 0.3)
            imgui.push_style_color(imgui.COLOR_BUTTON_HOVERED, 1.0, 1.0, 1.0, 0.2)
            imgui.push_font(self.font_t1)

            imgui.set_cursor_pos((35, 0)) # type: ignore
            if imgui.button("graph://"):
                self.graph_view_local_function()
            imgui.same_line()

            for name in self._name_list_r:
                imgui.same_line()
                imgui.button( name )
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
            del(self.background)
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
