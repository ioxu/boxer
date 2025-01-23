import pyglet
import pyglet.gl as gl
from pyglet.window import mouse
import boxer.shaping
#import boxer.shaders

class Mouse(pyglet.window.MouseCursor):
    def __init__(self):
        print("starting %s"%self)

        self.is_sheet_panning = False
        self.position = pyglet.math.Vec2()
        self.world_position = pyglet.math.Vec3()
        self.captured_by_ui = False

        self.label_screen_position = pyglet.text.Label( "s: ",
                                        font_name='Verdana',
                                        font_size=7.5,
                                        x=10,y=10,
                                        color=(255, 255, 255, 50)
                                    )

        self.label_world_position = pyglet.text.Label( "w: ",
                                        font_name='Verdana',
                                        font_size=7.5,
                                        x=10,y=10,
                                        color=(255, 230, 80, 50)
                                    )

        self.pointer = pyglet.shapes.Circle(0,0,5,16, (255, 0, 0, 128), batch = None)

        self._camera_transform : pyglet.math.Mat4 = pyglet.math.Mat4()
        self.camera_zoom : float = 1.0


    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers ):
        #print("mouse.on_mouse_drag %s"%buttons)
        self.update_position(x,y)
        if buttons & mouse.MIDDLE:
            self.is_sheet_panning = True


    def on_mouse_press(self, x, y, buttons, modifiers ):
        #print(self, self.mouse_press)
        #print("mouse.on_mouse_press %s"%buttons)
        if buttons & mouse.MIDDLE:
            self.is_sheet_panning = True


    def on_mouse_release(self, x, y, buttons, modifiers ):
        #print("mouse.on_mouse_release: %s"%buttons)
        if buttons & mouse.MIDDLE:
            self.is_sheet_panning = False
               

    def on_mouse_motion(self, x,y,ds,dy):
        self.update_position(x,y)


    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        # mouse wheel seems to only be on scroll_y
        self.update_position(x,y)


    def update_position(self, x,y):
        #print("mouse update_position %s %s"%(x,y))
        # self.position.x = x
        # self.position.y = y
        self.position = pyglet.math.Vec2( x, y )
        self.pointer.x = x
        self.pointer.y = y

        # calc world position
        spos = pyglet.math.Mat4.from_translation( pyglet.math.Vec3( self.position.x, self.position.y, 0.0 ) )
        wpos = ( ~self._camera_transform @ spos ).column(3)[:3]
        # self.world_position.x, self.world_position.y, self.world_position.z = wpos[0], wpos[1], wpos[2]
        self.world_position = pyglet.math.Vec3( wpos[0], wpos[1], wpos[2] )


    def draw(self, x, y):
        #print("mouse.draw %s %s"%(x,y))
        if self.is_sheet_panning:
            self.pointer.radius = 5
        else:
            self.pointer.radius = 3
        self.pointer.draw()

        self.label_screen_position.x = x+5
        self.label_screen_position.y = y+5
        self.label_screen_position.text = "s: %s, %s"%(self.position.x, self.position.y)
        self.label_screen_position.draw()

        self.label_world_position.x = x+5
        self.label_world_position.y = y-7
        self.label_world_position.text = "w: %0.1f, %0.1f"%(self.world_position.x, self.world_position.y)
        self.label_world_position.draw()


    def on_camera_transform_changed(self, transform : pyglet.math.Mat4 ) -> None:
        """desgined to recieve signal 'transform_changed' as emitted by Camera
        connect with 
            self.camera.push_handlers(transform_changed=self.mouse.on_camera_transform_changed)
        """
        self._camera_transform = transform
        self.camera_zoom =transform.column(0)[0]

