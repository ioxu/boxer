# boxer
workflow tool


# Containers

A tree of **Containers** is made by adding children to a single root **Container** using ``.add_child()``

Once a tree is constructed, call ``.update_structure()`` to initialise the tree's knowledge of itself. This identifies leaves, calculates node depth and unique ids, et cetera.

Before a tree is drawn, call ``.update_geometries()`` on the root **Container**.

Call ``.update_geometries()`` in the ``window.on_resize()`` event

## Containers class diagram


```mermaid
classDiagram
    class Container:::styleClass
    Container: +string name
    Container: +pyglet.window.Window window
    Container: +List children
    Container: -get_available_size_from_parent() tuple
    Container: -get_child_size() tuple
    Container: -get_child_position() tuple
    Container: +add_child() None
    Container: +update_geometries() None
    Container: +update_structure() None

    callback Container "callbackFunction" "base Container class, not abstract."

    class ViewportContainer["ViewportContainer"]
    ViewportContainer: +boxer.Camera camera

    Container <|-- HSplitContainer
    Container <|-- VSplitContainer
    Container <|-- ViewportContainer

    class Camera["Camera"]
    ViewportContainer o-- Camera

```

