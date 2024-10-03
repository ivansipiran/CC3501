#version 330

in vec3 fragPos;
in vec2 fragTexCoord;
in vec3 fragNormal;

out vec4 outColor;

uniform sampler2D u_texture;

void main() {
    outColor =  texture(u_texture, fragTexCoord);
}
