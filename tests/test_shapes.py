import boxer.shapes

def test_rectangle_centered_vertices():
    verts = boxer.shapes.rectangle_centered_vertices(5.5, 2.3, 11, 15)
    print("verts: %s"%str(verts))
    assert verts == (0.0, -5.2, 0.0, 11.0, -5.2, 0.0, 11.0, 9.8, 0.0, 0.0, 9.8, 0.0)

