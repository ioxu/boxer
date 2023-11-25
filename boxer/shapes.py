import pyglet.shapes

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


def rectangle_centered_vertices( centre_x:float, centre_y:float, width:float, height:float ) -> tuple:
    """
    Create counter-clockwise vertices for a 2d rectangle centred on a position, on the XY plane
    
    The vertex order is [0,1,2,3]

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


def quad_texcoords( scale_u : float = 1.0, scale_v : float = 1.0, offset_u : float = 0.0, offset_v : float = 0.0) -> tuple:
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



