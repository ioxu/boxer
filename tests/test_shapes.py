import boxer.shapes

# rectangle_centred_vertices

def test_rectangle_centered_vertices() -> None:
    verts = boxer.shapes.rectangle_centered_vertices(5.5, 2.3, 11, 15)
    print("verts: %s"%str(verts))
    assert verts == (0.0, -5.2, 0.0, 11.0, -5.2, 0.0, 11.0, 9.8, 0.0, 0.0, 9.8, 0.0)


#quad_texcoords

def test_quad_texcoords_offset() -> None:
    tex_coords = boxer.shapes.quad_texcoords( 1.0, 1.0, 0.5, 0.5 )
    assert tex_coords == ( 0.5, 0.5, 0.0,
                          1.5, 0.5, 0.0,
                          1.5, 1.5, 0.0,
                          0.5, 1.5, 0.0)
    
def test_quad_texcoords_scale() -> None:
    tex_coords = boxer.shapes.quad_texcoords( 3.3, 2.75, 0.0, 0.0 )
    assert tex_coords == ( 0.0, 0.0, 0.0,
                          3.3, 0.0, 0.0,
                          3.3, 2.75, 0.0,
                          0.0, 2.75, 0.0)
    
def test_quad_tecoords_scale_and_offset() -> None:
    tex_coords = boxer.shapes.quad_texcoords( 3.3, 2.75, 0.2, 0.35 )
    assert tex_coords == ( 0.2, 0.35, 0.0, 
                        3.5, 0.35, 0.0,
                        3.5, 3.1, 0.0,
                        0.2, 3.1, 0.0)


