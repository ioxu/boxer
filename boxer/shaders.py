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


# texture colour mixer shaders (TCMix) -----------------------------------------
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


# marching lines shaders -------------------------------------------------------

_MarchingLines_vertex_source ="""#version 330 core
    in vec3 position;
    in vec4 colors;
    out vec4 vertex_colors;
    out vec4 user_data;
    out vec2 sposition;

    uniform WindowBlock
    {
        mat4 projection;
        mat4 view;
    } window;  

    void main()
    {
        gl_Position = window.projection * window.view * vec4(position, 1.0);
        sposition = position.xy;
        vertex_colors = colors;
    }
"""


# vec2 bl = step(vec2(0.1),st);       // bottom-left
# vec2 tr = step(vec2(0.1),1.0-st);   // top-right
# color = vec3(bl.x * bl.y * tr.x * tr.y);

_MarchingLines_fragment_source = """#version 330 core
    in vec4 vertex_colors;
    in vec2 sposition;
    out vec4 final_color;

    uniform vec4 color_one;
    uniform float time;

    vec2 st = sposition;//gl_FragCoord.xy;///u_resolution.xy;
    // box
    uniform vec2 ir_bl;
    uniform vec2 ir_tr;
    uniform float positive;

    vec2 box_bl = step( ir_bl, st );
    vec2 box_tr = vec2(1.0)-step( ir_tr, st );
    float box_shape = box_bl.x * box_bl.y * box_tr.x * box_tr.y;
    float box = mix(box_shape, 1.0 - box_shape, step(positive, 0.5));

    // lines
    float line_width = 25.0 * 2;
    float diagonal = mod( ((gl_FragCoord.x+time) - gl_FragCoord.y)*(1.0/line_width) , 1.0);
    float d1 = smoothstep( 0.45, 0.5, diagonal );
    float d2 = smoothstep( 1.0, 0.95, diagonal );
    float line = d1*d2;

    vec4 col2 = vec4( 1.0, 1.0, 1.0, line * box  );

    void main()
    {
        final_color = color_one * col2 * vertex_colors;
        //final_color = vec4(st * .001, 0.0, 1.0) * vertex_colors;
    }
"""

def get_marchinglines_shader():
    """
    """
    _vert_shader = pyglet.graphics.shader.Shader(_MarchingLines_vertex_source, 'vertex')
    _frag_shader = pyglet.graphics.shader.Shader(_MarchingLines_fragment_source, 'fragment')
    program = pyglet.graphics.shader.ShaderProgram(_vert_shader, _frag_shader)
    return program