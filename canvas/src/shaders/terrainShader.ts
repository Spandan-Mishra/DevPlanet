import * as THREE from 'three'
import { simplexNoise3DGLSL } from './noise3D.glsl'
import type { ElevationRampNode, SurfaceMaterialGenome, TopologyGenome } from '@/types/genome'

export interface TerrainUniforms {
  [key: string]: THREE.IUniform
  uBaseRadius: { value: number }
  uMaxAltitude: { value: number }
  uSeaLevel: { value: number }
  uOctaves: { value: number }
  uPersistence: { value: number }
  uLacunarity: { value: number }
  uDomainWarpFrequency: { value: number }
  uDomainWarpAmplitude: { value: number }
  uLandformCenters: { value: THREE.Vector3[] }
  uLandformParams: { value: THREE.Vector3[] } // (plateRadius, elevationFactor, roughness)
  uLandformCount: { value: number }
  uElevationRamp: { value: THREE.Vector4[] } // (r, g, b, elevation)
  uRampStopsCount: { value: number }
  uSunDirection: { value: THREE.Vector3 }
  uAmbientLight: { value: THREE.Color }
  uSunColor: { value: THREE.Color }
  uMetallicFactor: { value: number }
}

export const terrainVertexShader = /* glsl */ `
${simplexNoise3DGLSL}

uniform float uBaseRadius;
uniform float uMaxAltitude;
uniform float uSeaLevel;
uniform int uOctaves;
uniform float uPersistence;
uniform float uLacunarity;
uniform float uDomainWarpFrequency;
uniform float uDomainWarpAmplitude;

uniform vec3 uLandformCenters[16];
uniform vec3 uLandformParams[16]; // (radius, elevationFactor, roughness)
uniform int uLandformCount;

varying vec3 vNormal;
varying vec3 vWorldPosition;
varying float vElevation; // Normalized [0.0, 1.0]

void main() {
  vec3 unitPos = normalize(position);

  // 1. Base Fractal Brownian Motion Terrain Noise
  float baseNoise = fbm(
    unitPos * 2.5,
    uOctaves,
    uPersistence,
    uLacunarity,
    uDomainWarpFrequency,
    uDomainWarpAmplitude
  );

  // 2. Continental Landform Plate Uplift & Influence
  float landformUplift = 0.0;
  for (int i = 0; i < 16; i++) {
    if (i >= uLandformCount) break;
    vec3 center = uLandformCenters[i];
    float radius = uLandformParams[i].x;
    float elevFactor = uLandformParams[i].y;
    float roughness = uLandformParams[i].z;

    // Great circle angular distance on unit sphere
    float dist = acos(clamp(dot(unitPos, center), -1.0, 1.0));
    if (dist < radius) {
      float t = 1.0 - (dist / radius);
      float bell = t * t * (3.0 - 2.0 * t); // Smoothstep bell curve
      float localNoise = snoise(unitPos * (4.0 + roughness * 8.0)) * 0.25;
      landformUplift += (bell * elevFactor) * (0.8 + localNoise);
    }
  }

  // Combined elevation metric normalized between 0.0 and 1.0
  float finalElevation = clamp(baseNoise * 0.6 + landformUplift * 0.4, 0.0, 1.0);
  vElevation = finalElevation;

  // Radial displacement calculation
  float displacement = 0.0;
  if (finalElevation > uSeaLevel) {
    float landFraction = (finalElevation - uSeaLevel) / max(0.001, (1.0 - uSeaLevel));
    displacement = landFraction * uMaxAltitude;
  }

  vec3 displacedPosition = unitPos * (uBaseRadius + displacement);
  vWorldPosition = (modelMatrix * vec4(displacedPosition, 1.0)).xyz;
  vNormal = normalize(normalMatrix * unitPos);

  gl_Position = projectionMatrix * modelViewMatrix * vec4(displacedPosition, 1.0);
}
`

export const terrainFragmentShader = /* glsl */ `
uniform vec4 uElevationRamp[6]; // rgb in xyz, elevation stop in w
uniform int uRampStopsCount;
uniform float uSeaLevel;
uniform vec3 uSunDirection;
uniform vec3 uAmbientLight;
uniform vec3 uSunColor;
uniform float uMetallicFactor;

varying vec3 vNormal;
varying vec3 vWorldPosition;
varying float vElevation;

// Multi-stop piecewise linear color ramp interpolation
vec3 evaluateElevationRamp(float elevation) {
  if (elevation <= uElevationRamp[0].w) {
    return uElevationRamp[0].xyz;
  }

  for (int i = 0; i < 5; i++) {
    if (i >= uRampStopsCount - 1) break;
    float stopA = uElevationRamp[i].w;
    float stopB = uElevationRamp[i + 1].w;

    if (elevation >= stopA && elevation <= stopB) {
      float t = (elevation - stopA) / max(0.0001, (stopB - stopA));
      return mix(uElevationRamp[i].xyz, uElevationRamp[i + 1].xyz, t);
    }
  }

  return uElevationRamp[min(uRampStopsCount - 1, 5)].xyz;
}

void main() {
  vec3 norm = normalize(vNormal);
  vec3 lightDir = normalize(uSunDirection);

  // Surface albedo color from procedural Oklab-derived elevation ramp
  vec3 albedo = evaluateElevationRamp(vElevation);

  // Directional Lambertian diffuse lighting
  float NdotL = max(dot(norm, lightDir), 0.0);
  vec3 diffuse = uSunColor * NdotL;

  // View-dependent specular highlight
  vec3 viewDir = normalize(cameraPosition - vWorldPosition);
  vec3 halfVector = normalize(lightDir + viewDir);
  float NdotH = max(dot(norm, halfVector), 0.0);
  float specularIntensity = pow(NdotH, 32.0) * (uMetallicFactor * 0.5);
  vec3 specular = uSunColor * specularIntensity;

  // Composite final shading
  vec3 finalColor = albedo * (uAmbientLight + diffuse) + specular;

  gl_FragColor = vec4(finalColor, 1.0);

  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`

export function createTerrainMaterial(
  topology: TopologyGenome,
  surfaceMaterial: SurfaceMaterialGenome
): THREE.ShaderMaterial {
  // Parse landform nodes into uniform arrays (capped at 16)
  const maxLandforms = 16
  const landformCenters: THREE.Vector3[] = []
  const landformParams: THREE.Vector3[] = []

  for (let i = 0; i < maxLandforms; i++) {
    const node = topology.landforms[i]
    if (node) {
      landformCenters.push(
        new THREE.Vector3(
          node.plateCenter[0],
          node.plateCenter[1],
          node.plateCenter[2]
        )
      )
      landformParams.push(
        new THREE.Vector3(node.plateRadius, node.elevationFactor, node.roughness)
      )
    } else {
      landformCenters.push(new THREE.Vector3(0, 1, 0))
      landformParams.push(new THREE.Vector3(0, 0, 0))
    }
  }

  // Normalize elevation color ramp to exactly 6 uniform slots
  const rawRamp = surfaceMaterial.elevationColorRamp || []
  const safeStops: ElevationRampNode[] = []
  if (rawRamp.length === 0) {
    safeStops.push({ elevation: 0.0, oklab: [0.5, 0, 0], hex: '#334455' })
  } else {
    for (let i = 0; i < Math.min(rawRamp.length, 6); i++) {
      safeStops.push(rawRamp[i])
    }
  }
  const lastStop = safeStops[safeStops.length - 1]
  while (safeStops.length < 6) {
    safeStops.push({ ...lastStop })
  }

  const elevationRamp: THREE.Vector4[] = safeStops.map(
    (stop: ElevationRampNode) => {
      const color = new THREE.Color(stop.hex)
      return new THREE.Vector4(color.r, color.g, color.b, stop.elevation)
    }
  )
  const rampStopsCount = Math.max(1, Math.min(rawRamp.length, 6))

  const uniforms: TerrainUniforms = {
    uBaseRadius: { value: topology.baseRadius },
    uMaxAltitude: { value: topology.maxAltitude },
    uSeaLevel: { value: topology.seaLevel },
    uOctaves: { value: topology.octaves },
    uPersistence: { value: topology.persistence },
    uLacunarity: { value: topology.lacunarity },
    uDomainWarpFrequency: { value: topology.domainWarpFrequency },
    uDomainWarpAmplitude: { value: topology.domainWarpAmplitude },
    uLandformCenters: { value: landformCenters },
    uLandformParams: { value: landformParams },
    uLandformCount: { value: topology.landforms.length },
    uElevationRamp: { value: elevationRamp },
    uRampStopsCount: { value: rampStopsCount },
    uSunDirection: { value: new THREE.Vector3(500, 200, 300).normalize() },
    uAmbientLight: { value: new THREE.Color('#3a4b5c') },
    uSunColor: { value: new THREE.Color('#ffffff') },
    uMetallicFactor: { value: surfaceMaterial.metallicFactor },
  }

  return new THREE.ShaderMaterial({
    uniforms,
    vertexShader: terrainVertexShader,
    fragmentShader: terrainFragmentShader,
    wireframe: false,
  })
}
