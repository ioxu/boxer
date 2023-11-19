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
        self.colour_one = (0.25, 0.25, 0.25)
        self.colour_two = (0.5, 0.5, 0.5)

        self.image = pyglet.image.load('boxer/resources/background_grid_map.png')
        self.texture : pyglet.image.Texture = pyglet.image.TileableTexture.create_for_image( self.image )
        #self.texture : pyglet.image.Texture = self.image.get_texture()
 
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER,
                gl.GL_LINEAR_MIPMAP_LINEAR)
        gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_LOD_BIAS, 0)

        self.position = pyglet.math.Vec2()

        print("starting %s"%self)

        _program = boxer.shaders.get_default_shader()
        self.shader_program = boxer.shaders.get_texture_colour_mix_shader() #boxer.shaders.get_default_textured_shader()

        # print("boxer.background shader attributes:")
        # print("boxer.background shader: %s"%str(self.shader_program))
        # print( self.shader_program.attributes )
        # print("boxer.background shader uniforms: %s"%str(self.shader_program.uniforms.items() ))

        self.shader_program['color_one'] = (*self.colour_one, 1.0)
        self.shader_program['color_two'] = (*self.colour_two, 1.0)

        _bg_width = 2000000
        _bg_height = _bg_width
        _bg_verts = boxer.shapes.rectangle_centered_vertices( 0.0, 0.0, _bg_width, _bg_width )
        _bg_tex_coords = boxer.shapes.quad_texcoords( _bg_width/self.texture.width, _bg_height/self.texture.height, 0.0, 0.0 )
        self.background_triangles = self.shader_program.vertex_list_indexed( 4, gl.GL_TRIANGLES, (0,1,2,0,2,3), self.batch, None,
                                    position = ('f', _bg_verts ),
                                    #colors = ('f', self.colour * 4 ),
                                    colors = ('f', (1.0, 1.0, 1.0, 1.0) * 4 ),
                                    tex_coords = ('f', _bg_tex_coords) )

        self.centre_point = _program.vertex_list_indexed(1, gl.GL_POINTS, [0], batch = self.batch,
                                position=('f', (0.0, 0.0, 0.0)),
                                colors = ('f', (1.0, 0.0, 0.0, 0.5) ))


    def set_colour_one(self, colour) -> None:
        self.colour_one = colour[:3]
        self.shader_program['color_one'] = (*self.colour_one, 1.0)


    def set_colour_two(self, colour) -> None:
        self.colour_two = colour[:3]
        self.shader_program['color_two'] = (*self.colour_two, 1.0)


    def draw(self):
        # preserving old immediate mode transform statements for reference
        # gl.glColor4f( *self.colour )
        # gl.glPushMatrix()
        # gl.glTranslatef(self.position.x, self.position.y, 0)
        
        gl.glEnable(self.texture.target)
        gl.glBindTexture(self.texture.target, self.texture.id)
        
        # gl.glGenerateMipmap(gl.GL_TEXTURE_2D)
        # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER,
        #         gl.GL_LINEAR_MIPMAP_LINEAR)
        # gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_LOD_BIAS, 0)
            
        gl.glPointSize(100)
        self.batch.draw()
        gl.glBindTexture(self.texture.target, 0)
        # gl.glPopMatrix()


    def as_json(self) -> dict:
        return {
            "name": self.name,
            "type": str(type(self)),
            "colour_one": self.colour_one,
            "colour_two": self.colour_two,
        }