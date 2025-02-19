import pyglet
import pyglet.gl as gl
import pyglet.image

import boxer.shaders
import boxer.shapes

from  colour import Color

import math, random
import uuid

import gc
import weakref

class BackgroundGroup( pyglet.graphics.Group ):
    """group to activate texturing and texture mix shader"""
    def __init__(self, order, texture, shaderprogram):
        super().__init__(order)
        self.texture = texture
        self.program = shaderprogram
        self.background_object = None #background_object
        
        self.id = uuid.uuid4()#random.random()

        self.originx = 0
        self.originy =0
        self.width = 200
        self.height= 200


    # def set_background(self, background) -> None:
    #     self.background_object = background


    def set_state(self):

        # print(f"    -- {self} {self.id} {self.program}")
        self.program.use()
        # self.background_object.shader_program['camera_matrix'] = self.background_object.camera_matrix
        gl.glEnable(self.texture.target)
        gl.glBindTexture(self.texture.target, self.texture.id)

        gl.glEnable(gl.GL_SCISSOR_TEST)
        gl.glScissor(int(self.originx),
                     int(self.originy),
                     int(self.width),
                     int(self.height))
    

    def unset_state(self):
        # print("--")
        # gl.glDisable(gl.GL_SCISSOR_TEST)
        gl.glBindTexture(self.texture.target, 0)
        self.program.stop()
        gl.glDisable(gl.GL_SCISSOR_TEST)


    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
            self.id == other.id)


    def __hash__(self):
        return hash(self.id)


    def __del__(self) -> None:
        print("DELETING GROOOOOOOOOOUUUUUUUUUUUUUPPPPPPPP")



class Background:
    """backround object for graph sheets"""

    def __init__(self,
                 name="background",
                 batch = None,
                 ): #parent_group = None):
        self.batch = batch or pyglet.graphics.Batch()
        # self.parent_group = parent_group or pyglet.graphics.Group()
        self.name = name
        c1 = Color(hsl=(random.random(), 0.15, 0.3))
        c2 = Color(hsl=(c1.hue + 0.2 , 0.15, 0.4))
        self.colour_one = c1.rgb #(0.25, 0.25, 0.25)
        self.colour_two = c2.rgb #(0.5, 0.5, 0.5)



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

        pyglet.clock.schedule_interval_soft(self.on_update, 1/60.0)
        self.age = 0.0
        self.speed = (random.random() - 0.5) * 10
        self.camera_matrix = pyglet.math.Mat4()
        self.shader_program['camera_matrix'] = pyglet.math.Mat4.from_translation( pyglet.math.Vec3( -1.0, 1.0, 0.0 ) )


        _bg_width = 2000000
        _bg_height = _bg_width
        _bg_verts = boxer.shapes.rectangle_centered_vertices( -0.5, 0.5, _bg_width, _bg_width )
        _bg_tex_coords = boxer.shapes.quad_texcoords( _bg_width/self.texture.width, _bg_height/self.texture.height, 0.0, 0.0 )

        self.group = BackgroundGroup( 0, self.texture , self.shader_program)#, self) #, parent = self.parent_group)

        self.background_triangles = self.shader_program.vertex_list_indexed( 4, gl.GL_TRIANGLES, (0,1,2,0,2,3),
                                    self.batch,
                                    self.group,
                                    position = ('f', _bg_verts ),
                                    #colors = ('f', self.colour * 4 ),
                                    colors = ('f', (1.0, 1.0, 1.0, 1.0) * 4 ),
                                    tex_coords = ('f', _bg_tex_coords) )




        # self.centre_point = _program.vertex_list_indexed(1, gl.GL_POINTS, [0], batch = self.batch,
        #                         position=('f', (0.0, 0.0, 0.0)),
        #                         colors = ('f', (1.0, 0.0, 0.0, 0.5) ))

    def on_update(self, dt):
        self.age += dt
        m = 50.0
        self.camera_matrix = pyglet.math.Mat4.from_translation(
            pyglet.math.Vec3( math.sin(self.age*self.speed)*m, math.cos(self.age*self.speed)*m, 0.0 ) )        
        self.shader_program['camera_matrix'] = self.camera_matrix
        # print(f"-- set matrix {self.camera_matrix}")
        # print(f"{self.speed} {hash(self.shader_program)}")


    def __del__(self) -> None:
        print("------------")
        print(f"DELETING BACKGROUND {self}")
        print(f" -> vertex list count {self.background_triangles.index_count}")
        self.background_triangles.delete()
        self.background_triangles = None
        # print(f" -> vertex list count {self.background_triangles.index_count}")
        print("------------")
        ref = gc.get_referrers( self.group )
        for i in ref:
            print(f"{type(i)} : {i}")
            if type(i) == type([]):
                for li in i:
                    print(f"    {li}")
            elif type(i)== type({}):
                for k in i:
                    print(f"    {k} : {i[k]}")
        
        # del(self.group)
        print(f" -> {self.group}")
        self.group = None
        print(f" -> {self.group}")
        print(f" -> {self.background_triangles}")
        # print(f" -> {self.background_triangles.index_count}")
        print("------------")


        # ref = gc.get_referrers( self.group )
        # for i in ref:
        #     print(i)
        # print("------------")




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


    def set_scissor(self, ox, oy, width, height) -> None:
        self.group.originx = ox
        self.group.originy = oy
        self.group.width = width
        self.group.height = height


    def as_json(self) -> dict:
        return {
            "name": self.name,
            "type": str(type(self)),
            "colour_one": self.colour_one,
            "colour_two": self.colour_two,
        }