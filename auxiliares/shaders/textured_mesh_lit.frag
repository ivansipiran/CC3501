#version 330

/* 
ESTE ARCHIVO VA A MODIFICARSE EN EL FUTURO
NO UTILIZAR PARA LAS TAREAS AÚN
*/

in vec3 fragColor;
in vec2 fragTexCoord;
in vec3 fragNormal;

out vec4 outColor;

uniform sampler2D u_texture;
uniform vec3 u_lightDir;
uniform vec3 u_lightColor;

float AMBIENT = 0.15f;

float computeLight(vec3 normal, vec3 lightDir)
{
    float diffuse = max(dot(normal, lightDir), 0.0);
    return diffuse;
}

void main()
{
    vec3 normal = normalize(fragNormal);
    float diffuse = computeLight(normal, u_lightDir);
    vec4 texel = texture(u_texture, fragTexCoord);
    if (texel.a < 0.5)
        discard;
    vec4 color = vec4(fragColor, 1.0f) * texel * max(diffuse, AMBIENT);
    outColor = color * vec4(u_lightColor, 1.0f);
}