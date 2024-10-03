#version 330

in vec3 position;
in vec2 texCoord;
in vec3 normal;

uniform mat4 u_model = mat4(1.0);
uniform mat4 u_view = mat4(1.0);
uniform mat4 u_projection = mat4(1.0);

out vec3 fragPos;
out vec2 fragTexCoord;
out vec3 fragNormal;

void main() {
    fragPos = vec3( u_model * vec4(position, 1.0f) );
    fragTexCoord = texCoord;
    fragNormal = mat3(transpose(inverse(u_model))) * normal;
    gl_Position = u_projection * u_view * u_model * vec4(position, 1.0f);
}
