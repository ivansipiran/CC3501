#version 330

in vec3 fragColor;
in vec2 fragTexCoord;
out vec4 outColor;

uniform sampler2D u_texture;

void main()
{
    vec4 texel = texture(u_texture, fragTexCoord);
    if (texel.a < 0.5)
        discard;
    outColor = vec4(fragColor, 1.0f) * texel;
}