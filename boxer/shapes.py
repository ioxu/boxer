import pyglet.shapes
from pyglet import gl

# custom boxer shapes
# (batch and group control)
# (vertex lists)
# (shaders)

# box
# rounded box
# bezier
# arc
# circle
# elipse
# speech bubble

# geometry forms:
# gl lines
# triangle strpis with width and UVs, textureable


class Arc( pyglet.shapes.Arc ):
    """pyglet.shapes.Arc doesn't draw properly??
    """
    def draw(self):
        self._group.set_state_recursive()
        self._vertex_list.draw(self._draw_mode)
        self._group.unset_state_recursive()


class RectangleLine( pyglet.shapes.Rectangle ):
    def __init__(self,  x, y, width, height,
                line_width,
                color=(255, 255, 255, 255),
                batch=None,
                group=None):
        # pyglet.shapes.Rectangle(self,  x, y, width, height, **kwargs)
        # super().__init__(x,y, width, height, **kwargs)
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._rotation = 0
        self._num_verts = 24

        self._line_width = line_width

        r, g, b, *a = color
        self._rgba = r, g, b, a[0] if a else 255

        program = pyglet.shapes.get_default_shader()
        self._batch = batch or pyglet.graphics.Batch()
        self._group = self.group_class(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA, program, group)

        self._create_vertex_list()


    def _create_vertex_list(self):
        verts = self._get_vertices()
        print("HERE %s (length: %s)"%(verts, len(verts)))
        self._vertex_list = self._group.program.vertex_list(
            self._num_verts, self._draw_mode, self._batch, self._group,
            position=('f', self._get_vertices()),
            colors=('Bn', self._rgba * self._num_verts),
            translation=('f', (self._x, self._y) * self._num_verts))


    def _get_vertices(self):
        if not self._visible:
             return (0, 0) * self._num_verts
        else:
            half_width = self._line_width / 2.0
            
            # x1 = -self._anchor_x - half_width
            # y1 = -self._anchor_y - half_width
            # x2 = x1 + self._width + half_width
            # y2 = y1 + self._height + half_width

            x1 = -self._anchor_x
            y1 = -self._anchor_y
            x2 = x1 + self._width
            y2 = y1 + self._height


            x3 = x1 + half_width
            y3 = y1 + half_width
            x4 = x2 - half_width
            y4 = y2 - half_width

            return  x1, y1, x2, y1, x4, y3,\
                    x1, y1, x4, y3, x3, y3,\
                    x2, y1, x2, y2, x4, y4,\
                    x2, y1, x4, y4, x4, y3,\
                    x2, y2, x1, y2, x3, y4,\
                    x2, y2, x3, y4, x4, y4,\
                    x1, y1, x3, y3, x3, y4,\
                    x1, y1, x3, y4, x1, y2


    def _update_vertices(self):
        self._vertex_list.position[:] = self._get_vertices()


    @property
    def anchor_x(self):
        """The X coordinate of the anchor point

        :type: int or float
        """
        return self._anchor_x


    @anchor_x.setter
    def anchor_x(self, value):
        self._anchor_x = value
        self._update_vertices()


    @property
    def anchor_y(self):
        """The Y coordinate of the anchor point

        :type: int or float
        """
        return self._anchor_y


    @anchor_y.setter
    def anchor_y(self, value):
        self._anchor_y = value
        self._update_vertices()


    @property
    def anchor_position(self):
        """The (x, y) coordinates of the anchor point, as a tuple.

        :Parameters:
            `x` : int or float
                X coordinate of the anchor point.
            `y` : int or float
                Y coordinate of the anchor point.
        """
        return self._anchor_x, self._anchor_y


    @anchor_position.setter
    def anchor_position(self, values):
        self._anchor_x, self._anchor_y = values
        self._update_vertices()


def rectangle_centered_vertices(\
        centre_x:float,
        centre_y:float,
        width:float,
        height:float ) -> tuple:
    """
    Create counter-clockwise vertices for a 2d rectangle centred on a position, on the XY plane
    The vertex order is [0,1,2,3]
    Starting top left corner
    The index list for GL_TRIANGLES is [0,1,2,0,2,3]

    Arguments:
        `centre_x` : `float`
            the x coord of the centre of the rectangle
        `centre_y` : `float`
            the y coord of the centre of the rectangle
    """
    return (-width/2.0 + centre_x, -height/2.0 + centre_y, 0.0,
            width/2.0 + centre_x, -height/2.0 + centre_y, 0.0,
            width/2.0 + centre_x, height/2.0 + centre_y, 0.0,
            -width/2.0 + centre_x, height/2.0 + centre_y, 0.0 )


def quad_texcoords(
        scale_u : float = 1.0,
        scale_v : float = 1.0,
        offset_u : float = 0.0,
        offset_v : float = 0.0) -> tuple:
    """
    create counter-clockwise UVW vertices for texture coords for a quad, on the UV plane
    
    The vertex order is [0,1,2,3]

    the default quad is organised so

    3 *--------* 2 <- (1.0, 1.0, 0.0)
      |        |
      |        |
      |        |
    0 *--------* 1
    ^
    |
    (0.0, 0.0, 0.0)

    Scale (multiply) is applied before offset (addition)

    Arguments:
        `scale_u` : `float`
            scale of U dimension
        `scale_v` : `float`
            scale of V dimension
        `offset_u` : `float`
            offset in U
        `offset_v` : `float`
            offset in V
    """
    return ( 0.0 + offset_u, 0.0 + offset_v, 0.0,
             1.0 * scale_u + offset_u, 0.0 + offset_v, 0.0,
             1.0 * scale_u + offset_u, 1.0 * scale_v + offset_v, 0.0,
             0.0 + offset_u, 1.0 * scale_v + offset_v, 0.0)


# ------------------------------------------------------------------------------

def point_in_box( x, y, bottom_left_x, bottom_left_y, top_right_x, top_right_y ) -> bool:
    """test if point is inside a box
    :returns
        bool : True if inside box"""
    return bottom_left_x <= x <= top_right_x and bottom_left_y <= y <= top_right_y