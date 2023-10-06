#version 330

/* 
ESTE ARCHIVO VA A MODIFICARSE EN EL FUTURO
NO UTILIZAR PARA LAS TAREAS AÚN
*/

in vec3 position;
in vec2 texCoord;
in vec3 normal;

uniform vec3 u_color = vec3(1.0);

uniform mat4 u_model = mat4(1.0);
uniform mat4 u_view = mat4(1.0);
uniform mat4 u_projection = mat4(1.0);

out vec3 fragColor;
out vec2 fragTexCoord;
out vec3 fragNormal;

void main()
{
    fragColor = u_color;
    fragTexCoord = texCoord;
    fragNormal = mat3(transpose(inverse(u_model))) * normal;
    
    gl_Position = u_projection * u_view * u_model * vec4(position, 1.0f);
}