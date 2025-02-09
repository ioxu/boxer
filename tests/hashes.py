import pyglet
import sys
sys.path.extend("..")
from boxer import containers

batch_dict = {}

c1 = containers.ContainerView()
h_tuple = (c1, "/root/some_graph", containers.ContainerView)
print(f"immutable tuple: {h_tuple}")
h1 = hash( h_tuple )
print(f"hash: {h1}")

batch_dict[h1] = pyglet.graphics.Batch()

c2 = containers.ContainerView()
h_tuple2= (c2, "/root/a_much_deeper_path/child1", containers.ContainerView)
print(f"immutable tuple: {h_tuple2}")
h2 = hash( h_tuple2 )
print(f"hash (2): {h2}")

h_tuple3 = (c2, "/root/a_much_deeper_path/child1", containers.ContainerView)
h3 = hash( h_tuple3 )
print(f"hash (3): {h3}")



batch_dict[h2] = pyglet.graphics.Batch()

print(f"batch_dict: {batch_dict}")

print(f"fetch batch: {batch_dict[h1]}")
print(f"fetch batch: {batch_dict[h2]}")



