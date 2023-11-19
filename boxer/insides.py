# object introspection/reflection things

import inspect


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    print("insides.py tests")
    import sys
    sys.path.extend("..")
    import boxer.background
    bg = boxer.background.Background( name="test_background")
    print(bg)
    print("-----")
    for i in inspect.getmembers( bg ):
        if not i[0].startswith("__"):
            print(i, type(i[1]))
