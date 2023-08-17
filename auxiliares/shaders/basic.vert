#version 330

in vec2 position;
in vec3 color;
in float intensity;

out vec3 fragColor;
out float fragIntensity;

void main()
{
    fragColor = color;
    fragIntensity = intensity;
    gl_Position = vec4(position, 0.0f, 1.0f);
}