import pyglet
import pyglet.gl as gl
import pyglet.image

import boxer.shaders
import boxer.shapes

class Background:
    """backround object for graph sheets"""

    def __init__(self,
                 name="background"):
        self.batch = pyglet.graphics.Batch()
        self.name = name
        self.colour = (0.5, 0.5, 0.5, 1.0)
        self.image = pyglet.image.load('boxer/resources/background_grid_map.png')
        self.texture = pyglet.image.TileableTexture.create_for_image( self.image )
        self.position = pyglet.math.Vec2()

        print("starting %s"%self)

        _program = boxer.shaders.get_default_shader()
        _textured_program = boxer.shaders.get_default_textured_shader()

        # print("shader attributes:")
        # print( _textured_program.attributes )

        _bg_width = 2000000
        _bg_height = _bg_width
        _bg_verts = boxer.shapes.rectangle_centered_vertices( 0.0, 0.0, _bg_width, _bg_width )
        _bg_tex_coords = boxer.shapes.quad_texcoords( _bg_width/self.texture.width, _bg_height/self.texture.height, 0.0, 0.0 )
        self.background_triangles = _textured_program.vertex_list_indexed( 4, gl.GL_TRIANGLES, (0,1,2,0,2,3), self.batch, None,
                                    position = ('f', _bg_verts ),
                                    colors = ('f', self.colour * 4 ),
                                    tex_coords = ('f', _bg_tex_coords) )

        self.centre_point = _program.vertex_list_indexed(1, gl.GL_POINTS, [0], batch = self.batch,
                                position=('f', (0.0, 0.0, 0.0)),
                                colors = ('f', (1.0, 0.0, 0.0, 0.15) ))




    def draw(self):
        # preserving old immediate mode transform statements for reference
        # TODO: use new Mat4 methods 
        # gl.glColor4f( *self.colour )
        # gl.glPushMatrix()
        # gl.glTranslatef(self.position.x, self.position.y, 0)
        gl.glEnable(self.texture.target)
        gl.glBindTexture(self.texture.target, self.texture.id)
        gl.glPointSize(100)
        self.batch.draw()
        gl.glBindTexture(self.texture.target, 0)
        # gl.glPopMatrix()
