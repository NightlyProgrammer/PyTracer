#version 330 core

layout (location = 0) out vec3 fragColor;

in vec2 fragPos;

uniform sampler2D u_accumulatedTexture;
uniform vec2 u_screenSize;
uniform vec2[100] u_samplingPositions;
uniform int u_numSamplingPositions;

void main(){
    vec2 uv = fragPos * 0.5 + vec2(0.5);
    vec3 color = vec3(0);
    vec2 samplingOffset;
    for(int i = 0; i < u_numSamplingPositions; i++){
        samplingOffset = u_samplingPositions[i] / u_screenSize;
        color += texture2D(u_accumulatedTexture, uv + samplingOffset).rgb;
    }
    color = color / u_numSamplingPositions;

    float gamma = 2.2;
    color = pow(color, vec3(1.0 / gamma));
    fragColor = color;
}