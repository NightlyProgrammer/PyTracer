#version 330 core

#define PI 3.1415926
#define EPSILON 1.0e-10 // tiny val
#define MAX_NUM_RAYS 10

layout (location = 0) out vec3 fragColor;

in vec2 fragPos;

uniform float aspect_ratio;
uniform mat4 u_cameraTransformation;
uniform float u_fov;
uniform vec2 u_screenSize;
uniform uint u_numAccumulatedFrames;
uniform sampler2D u_resultBuffer;

struct Material{
    vec3 color;

    vec3 emissionColor;
    float emissionStrength;

    float roughness;
    float metallic;
};

struct HitInfo{
    bool hit;
    float distance;
    vec3 position;
    vec3 normal;
    Material material;
};

struct Ray{
    vec3 origin;
    vec3 direction;
};

struct Sphere{
    vec3 position;
    float radius;
    Material material;
};
uniform Sphere spheres[100];
uniform int spheres_length;



float raySphereIntersect(vec3 r0, vec3 rd, vec3 s0, float sr) {
    // - r0: ray origin
    // - rd: normalized ray direction
    // - s0: sphere center
    // - sr: sphere radius
    // - Returns distance from r0 to first intersecion with sphere,
    //   or -1.0 if no intersection.
    float a = dot(rd, rd);
    vec3 s0_r0 = r0 - s0;
    float b = 2.0 * dot(rd, s0_r0);
    float c = dot(s0_r0, s0_r0) - (sr * sr);
    if (b*b - 4.0*a*c < 0.0) {
        return -1.0;
    }
    return (-b - sqrt((b*b) - 4.0*a*c))/(2.0*a);
}
vec3 calcSphereNormal(vec3 s0, vec3 position){
    return normalize(position - s0);
}

uint getCurrentState(vec2 texelCoords, int screenWidth)
{
    uint pixelIndex = (uint(texelCoords.y) * uint(screenWidth)) + uint(texelCoords.x);
    return uint(pixelIndex + u_numAccumulatedFrames * uint(745621)); // new state every frame
}

/** The RandomValue function generates a random value between 0 and 1 using a simple linear congruential generator (LCG).
 * The function uses the LCG algorithm to generate a sequence of pseudo-random numbers based on a seed value.
 * Thanks to https://www.pcg-random.org, https://www.shadertoy.com/view/XlGcRh
 */
float RandomValue(inout uint state)
{
    
    state = state * 747796405u + 2891336453u;
    uint result = ((state >> ((state >> 28u) + 4u)) ^ state) * 277803737u;
    result = (result >> 22u) ^ result;
    return float(result) / 4294967295.0;
}

/** The RandomValueNormalDistribution function generates a random value from a normal distribution using the Box-Muller transform.
 * The function generates two random values from a uniform distribution and transforms them into a random value from a normal distribution.
 * Thanks to https://stackoverflow.com/a/6178290
 */
float RandomValueNormalDistribution(inout uint state)
{
    float theta = 2 * PI * RandomValue(state);
    float rho = sqrt(-2 * log(RandomValue(state)));
    return rho * cos(theta);
}

/** The RandomDirection function generates a random direction vector by sampling from a normal distribution in three dimensions.
 * The function generates three random values from a normal distribution and normalizes them to create a random direction vector.
 * Thanks to https://math.stackexchange.com/questions/1585975
 */
vec3 RandomDirection(inout uint state)
{
    float x = RandomValueNormalDistribution(state);
    float y = RandomValueNormalDistribution(state);
    float z = RandomValueNormalDistribution(state);
    return normalize(vec3(x, y, z));
}

/** The RandomDirectionInHemisphere function generates a random direction vector in the hemisphere defined by the normal vector.
 * The distribution is cosine-weighted. (meaning more rays are sent in the direction of the normal)
 */
vec3 RandomDirectionInHemisphere(vec3 normalVector, inout uint state)
{
    vec3 randomDirectionVector = RandomDirection(state);
    if (dot(normalVector, randomDirectionVector) < 0)
    {
        randomDirectionVector = -randomDirectionVector;
    }
    return randomDirectionVector;
}
HitInfo raytrace(Ray ray){
    HitInfo info;
    info.hit = false;
    info.distance = -1.0;
    float dist;
    for(int i = 0; i < spheres_length; i++){
        Sphere currentSphere = spheres[i];
        dist = raySphereIntersect(ray.origin, ray.direction, currentSphere.position, currentSphere.radius);
        if( dist>=0 && ((dist < info.distance) || !info.hit)){
            info.hit = (dist>=0);
            info.distance = dist;
            info.position = ray.origin + ray.direction * (dist);
            info.normal = calcSphereNormal(currentSphere.position, info.position);
            info.material = currentSphere.material;
        }
    }
    return info;
}

vec3 getSkyboxColor(vec3 direction){
    float factor = dot(direction, vec3(0, 1, 0)) * 0.5 + 0.5;
    vec3 color1 = vec3(0, 1, 1) * 0.2;
    vec3 color2 = vec3(1, 0.8, 0.5) * 0.2;
    //return vec3(0.0);
    return  color1 * factor + color2 * (1-factor);//direction * 0.5 + vec3(0.5);
}

vec3 calculateColor(Ray ray, inout uint state){
    HitInfo info;
    Material material;
    vec3 rayColor = vec3(1.0); //color of all the material ray reflects from
    vec3 rayBrightness = vec3(0.0);//holds data about emission
    vec3 normal;

    for(int i = 0; i <= MAX_NUM_RAYS; i++){
        info = raytrace(ray);
        if( info.hit ){
            material = info.material;
            ray.origin = info.position;

            //ray.direction = normalize(info.normal + RandomDirection(state));
            
            normal = normalize(info.normal + RandomDirectionInHemisphere(info.normal, state) * material.roughness);
            ray.direction = normalize(reflect(ray.direction, normal));
            ray.direction = ray.direction + normal * material.roughness;

            rayBrightness += info.material.emissionColor * info.material.emissionStrength * rayColor;
            rayColor *= info.material.color;
        }else {
            //didnt collide anymore so break out of loop early
            rayBrightness += getSkyboxColor(ray.direction) * rayColor;
            break;
        }
    }

    return rayBrightness;
}

void main(){
    float focal_length = 1.0 / tan(u_fov/2.0); //basically distance from eye/cam to screen

    vec2 uv = fragPos * 0.5 + vec2(0.5);
    uint randomState = getCurrentState(u_screenSize*uv, int(u_screenSize.x));

    vec2 fragPosAspectCorrect = fragPos * vec2(1.0, aspect_ratio);//correct for aspect ratio

    Ray ray;
    //applying transformations
    //ray.origin = ( vec4(fragPosAspectCorrect.xy, 0.0, 1.0) * u_cameraTransformation ).xyz;
    ray.origin = ( vec4(0.0, 0.0, 0.0, 1.0) * u_cameraTransformation ).xyz;
    ray.direction = vec3(fragPosAspectCorrect.xy, focal_length);
    ray.direction = (vec4(ray.direction, 0.0) * u_cameraTransformation).xyz;
    ray.direction = normalize(ray.direction);

    float weight = 1.0 / (int(u_numAccumulatedFrames) + 1);//calc average of past frames correctly

    vec3 accum_color = texture2D(u_resultBuffer, uv).rgb;
    
    vec3 color = calculateColor(ray, randomState);

    fragColor = color * weight + accum_color * (1.0 - weight);
}