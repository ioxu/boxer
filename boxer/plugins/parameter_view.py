import pyglet
import boxer.containers
import imgui
# import boxer.plugins.parameter_view

class ParameterView( boxer.containers.ContainerView ):
        string_name = "Parameters"

        imgui.create_context()
        io = imgui.get_io()
        font_t1 = io.fonts.add_font_from_file_ttf("boxer/resources/fonts/DejaVuSansCondensed.ttf", 12 )


        @classmethod
        def draw_class( cls ) -> None:
            print(f"draw_class {cls}")


        def __init__( self, batch = None ):
            print("instancing 'Parameters' ContainerView")
            self.batch = batch or pyglet.graphics.Batch()


            self.entered = False

            self.margin = 0
            self.bg_rect = pyglet.shapes.Rectangle(
                50, 50, 200, 200,
                #40, 8,
                (30, 30, 30, 180),
                pyglet.gl.GL_SRC_ALPHA,
                pyglet.gl.GL_ONE_MINUS_SRC_ALPHA,
                self.batch
            )
            self.circle = pyglet.shapes.Circle(
                 10,10,
                 10,32,
                 (255,30,30,200),
                pyglet.gl.GL_SRC_ALPHA,
                pyglet.gl.GL_ONE_MINUS_SRC_ALPHA,
                self.batch
            )
            self.mouse_circle = pyglet.shapes.Circle(
                 10,10,
                 5,32,
                 (30,255,30,100),
                pyglet.gl.GL_SRC_ALPHA,
                pyglet.gl.GL_ONE_MINUS_SRC_ALPHA,
                self.batch
            )

            self.view_label = pyglet.text.Label(
                "parameters",
                font_size = 15.0,
                color = (255,255,255, 40),
                x = 10, y = 20,
                batch=self.batch
            )


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
                print(f"CLICKED graph:// from {self}")

            imgui.pop_font() # _t1
            imgui.pop_style_color(3) # button colors
            imgui.pop_style_var(1) # item spacing
            imgui.pop_style_var(1) # rounded buttons            
            imgui.pop_style_var() # window padding


        def __del__(self) -> None:
            print(f"deleting GraphView {self}")
            self.bg_rect.delete()
            self.circle.delete()
            self.mouse_circle.delete()
            self.view_label.delete()            
            # self.disconnect_handlers()
            super().__del__()


        def draw_instance(self) -> None:
            self.batch.draw()


        def update_geometries(self, container):
            super().update_geometries( container )

            m = self.margin
            self.bg_rect.position = pyglet.math.Vec2( container.position.x + m, container.position.y + m )
            self.bg_rect.width = container.width - (2*m)
            self.bg_rect.height = container.height - (2*m)
            self.circle.position = (container.position.x + container.width - 18.0, container.position.y + 18.0)

            # label
            self.view_label.position = pyglet.math.Vec3( container.position.x + 10, container.position.y + (self.view_label.content_height * 0.5) , 0 )


        def connect_handlers(self, target) -> None:
            self.entered = True
            self.mouse_circle.color = (*self.mouse_circle.color[:3], 100)
            target.push_handlers( on_mouse_motion=self.on_mouse_motion )


        def disconnect_handlers(self, target) -> None:
            self.entered = False
            self.mouse_circle.color = (*self.mouse_circle.color[:3], 0)
            target.remove_handlers( on_mouse_motion=self.on_mouse_motion )


        def on_mouse_motion( self, x, y, dx, dy ) -> None:
            # print(f"ParameterView.on_mouse_motion() {x} {y} {dx} {dy}")
            self.mouse_circle.position = pyglet.math.Vec2( x, y )
