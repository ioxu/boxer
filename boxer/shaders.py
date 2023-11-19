import pyglet

# basic shaders ----------------------------------------------------------------

_vertex_source = """#version 330 core
    in vec3 position;
    in vec4 colors;
    in vec3 tex_coords;
    out vec4 vertex_colors;
    out vec3 texture_coords;
    out vec4 user_data;
    
    uniform WindowBlock
    {
        mat4 projection;
        mat4 view;
    } window;  

    void main()
    {
        gl_Position = window.projection * window.view * vec4(position, 1.0);

        vertex_colors = colors;
        texture_coords = tex_coords;
    }
"""

_fragment_source = """#version 330 core
    in vec4 vertex_colors;
    in vec3 texture_coords;
    out vec4 final_colors;

    uniform sampler2D our_texture;

    void main()
    {
        final_colors = vertex_colors;    
    }
"""

_fragment_textured_source = """#version 330 core
    in vec4 vertex_colors;
    in vec3 texture_coords;
    out vec4 final_colors;

    uniform sampler2D our_texture;

    void main()
    {
        final_colors = texture(our_texture, texture_coords.xy) * vertex_colors;    
    }
"""

def get_default_shader():
    """
    default shader program with vertex colors
    """
    _default_vert_shader = pyglet.graphics.shader.Shader(_vertex_source, 'vertex')
    _default_frag_shader = pyglet.graphics.shader.Shader(_fragment_source, 'fragment')
    program = pyglet.graphics.shader.ShaderProgram(_default_vert_shader, _default_frag_shader)
    return program


def get_default_textured_shader():
    """
    default shader program with texturing, texture coords and vertex colors
    """
    _default_vert_shader = pyglet.graphics.shader.Shader(_vertex_source, 'vertex')
    _default_frag_shader = pyglet.graphics.shader.Shader(_fragment_textured_source, 'fragment')
    program = pyglet.graphics.shader.ShaderProgram(_default_vert_shader, _default_frag_shader)
    return program


# texture colour mixer shaders (TCMix) -------------------------------------------
# mix two colours based on values in a texture

_TCMix_vertex_source ="""#version 330 core
    in vec3 position;
    in vec4 colors;
    in vec3 tex_coords;
    out vec4 vertex_colors;
    out vec3 texture_coords;
    out vec4 user_data;
    
    uniform WindowBlock
    {
        mat4 projection;
        mat4 view;
    } window;  

    void main()
    {
        gl_Position = window.projection * window.view * vec4(position, 1.0);

        vertex_colors = colors;
        texture_coords = tex_coords;
    }
"""

_TCMix_fragment_source = """#version 330 core
    in vec4 vertex_colors;
    in vec3 texture_coords;
    out vec4 final_colors;

    uniform vec4 color_one;
    uniform vec4 color_two;

    uniform sampler2D our_texture;

    void main()
    {
        final_colors = mix( color_one, color_two, texture(our_texture, texture_coords.xy).r) * vertex_colors;    
    }
"""

def get_texture_colour_mix_shader():
    """
    colour mixing shader program with texturing, texture coords and vertex colors
    two uniforms control input colours:
    color_one
    color_two

    returns a mix by red channel of our_texture sampler2D
    """
    _default_vert_shader = pyglet.graphics.shader.Shader(_TCMix_vertex_source, 'vertex')
    _default_frag_shader = pyglet.graphics.shader.Shader(_TCMix_fragment_source, 'fragment')
    program = pyglet.graphics.shader.ShaderProgram(_default_vert_shader, _default_frag_shader)
    return program