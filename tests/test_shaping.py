import boxer.shaping

def test_shaping_remap() -> None:
    assert boxer.shaping.remap(0.5, 0.0, 1.0, 1.0, 2.0) ==  1.5

