
def rectangle_centered_vertices( centre_x:float, centre_y:float, width:float, height:float ) -> tuple:
    """
    create counter-clockwise vertices for a 2d rectangle centred on a position, on the XY plane
    
    Args:
        centre_x (float) : the x coord of the centre of the rectangle
        centre_y (float) : the y coord of the centre of the rectangle
    """
    return (-width/2.0 + centre_x, -height/2.0 + centre_y, 0.0,
            width/2.0 + centre_x, -height/2.0 + centre_y, 0.0,
            width/2.0 + centre_x, height/2.0 + centre_y, 0.0,
            -width/2.0 + centre_x, height/2.0 + centre_y, 0.0 )


