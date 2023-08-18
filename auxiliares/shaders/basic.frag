#version 330

in vec3 fragColor;
in float fragIntensity;
out vec4 outColor;

void main()
{
    outColor = fragIntensity * vec4(fragColor, 1.0f);
}