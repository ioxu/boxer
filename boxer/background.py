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
        print("starting %s"%self)


    def draw(self):
        gl.glColor4f( *self.colour )
        gl.glPushMatrix()
        gl.glTranslatef(self.x, self.y, 0)
        self.texture.blit_tiled(-1000000,-1000000,0,2000000,2000000)
        gl.glPointSize(50)
        pyglet.graphics.draw( 1, pyglet.gl.GL_POINTS,
			( 'v2i', ( 0, 0) ) )
        gl.glPopMatrix()
