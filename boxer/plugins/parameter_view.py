import pyglet
import boxer.containers
# import boxer.plugins.parameter_view

class ParameterView( boxer.containers.ContainerView ):
        string_name = "Parameters"
        def __init__( self, batch = None ):
            print("instancing 'Parameters' ContainerView")

            self.entered = False

            self.margin = 0
            self.bg_rect = pyglet.shapes.Rectangle(
                50, 50, 200, 200,
                #40, 8,
                (30, 30, 30, 180),
                pyglet.gl.GL_SRC_ALPHA,
                pyglet.gl.GL_ONE_MINUS_SRC_ALPHA,
                batch
            )
            self.circle = pyglet.shapes.Circle(
                 10,10,
                 10,32,
                 (255,30,30,200),
                pyglet.gl.GL_SRC_ALPHA,
                pyglet.gl.GL_ONE_MINUS_SRC_ALPHA,
                batch
            )
            self.mouse_circle = pyglet.shapes.Circle(
                 10,10,
                 5,32,
                 (30,255,30,100),
                pyglet.gl.GL_SRC_ALPHA,
                pyglet.gl.GL_ONE_MINUS_SRC_ALPHA,
                batch
            )

            self.view_label = pyglet.text.Label(
                "parameters",
                font_size = 15.0,
                color = (255,255,255, 40),
                x = 10, y = 20,
                batch=batch
            )


        def __del__(self) -> None:
            self.bg_rect.delete()
            self.circle.delete()
            self.mouse_circle.delete()
            self.view_label.delete()            
            # self.disconnect_handlers()


        def update_geometries(self, container):
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
