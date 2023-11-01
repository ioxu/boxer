import pyglet
import pyglet.gl as gl

class Background:
    """backround object for graph sheets"""

    def __init__(self,
                 name="background"):
        self.name = name
        self.colour = (0.5, 0.5, 0.5, 1.0)
        self.image = pyglet.image.load('boxer/resources/background_grid_map.png')
        self.texture = pyglet.image.TileableTexture.create_for_image( self.image )
        self.position = pyglet.math.Vec2()
        self.batch = pyglet.graphics.Batch()
        print("starting %s"%self)


        print(pyglet.graphics.get_default_shader().attributes.items())

        _program = pyglet.graphics.get_default_shader()

        self.centre_tri = _program.vertex_list_indexed(4, gl.GL_TRIANGLES, [0,1,2,0,2,3], self.batch, None,
                                position=('f', create_quad_vertex_list(250, 250, 0.0, 100.0, 100.0) ),
                                colors = ('f', (1.0, 0.0, 0.0, 1.0,  0.0, 1.0, 0.0, 1.0,  0.0, 0.0, 1.0, 1.0,  1.0, 1.0, 0.0, 1.0) ))

        self.centre_point = _program.vertex_list_indexed(1, gl.GL_POINTS, [0], batch = self.batch,
                                position=('f', (0.0, 0.0, 0.0)),
                                colors = ('f', (1.0, 0.0, 0.0, 0.15) ))


    def draw(self):
        # gl.glColor4f( *self.colour )
        # gl.glPushMatrix()
        # gl.glTranslatef(self.position.x, self.position.y, 0)
        self.texture.blit_tiled(-1000000,-1000000,0,2000000,2000000)
        gl.glPointSize(50)
        self.batch.draw()
        # gl.glPopMatrix()



def create_quad_vertex_list(x, y, z, width, height):
    return x, y, z, x + width, y, z, x + width, y + height, z, x, y + height, z
