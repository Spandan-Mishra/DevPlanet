import * as THREE from 'three'
import type { AtmosphereGenome } from '@/types/genome'

export interface AtmosphereUniforms {
  [key: string]: THREE.IUniform
  uRayleighCoeffs: { value: THREE.Vector3 } // (R, G, B) optical scattering coefficients
  uMieCoeff: { value: number }
  uMieG: { value: number }
  uDensityScaleHeight: { value: number }
  uSunDirection: { value: THREE.Vector3 }
}

export const atmosphereVertexShader = /* glsl */ `
varying vec3 vNormal;
varying vec3 vWorldPosition;

void main() {
  vNormal = normalize(normalMatrix * normal);
  vec4 worldPos = modelMatrix * vec4(position, 1.0);
  vWorldPosition = worldPos.xyz;
  gl_Position = projectionMatrix * viewMatrix * worldPos;
}
`

export const atmosphereFragmentShader = /* glsl */ `
uniform vec3 uRayleighCoeffs;
uniform float uMieCoeff;
uniform float uMieG;
uniform float uDensityScaleHeight;
uniform vec3 uSunDirection;

varying vec3 vNormal;
varying vec3 vWorldPosition;

// Henyey-Greenstein phase function for forward Mie aerosol scattering
float henyeyGreensteinPhase(float cosTheta, float g) {
  float g2 = g * g;
  return (1.0 - g2) / pow(max(0.001, 1.0 + g2 - 2.0 * g * cosTheta), 1.5) / (4.0 * 3.14159265);
}

// Rayleigh phase function for isotropic air molecule dispersion
float rayleighPhase(float cosTheta) {
  return 0.75 * (1.0 + cosTheta * cosTheta);
}

void main() {
  vec3 viewDir = normalize(cameraPosition - vWorldPosition);
  vec3 lightDir = normalize(uSunDirection);
  vec3 norm = normalize(vNormal);

  // Optical depth / grazing rim Fresnel factor
  float VdotN = max(dot(viewDir, norm), 0.0);
  float rim = 1.0 - VdotN;
  float opticalDensity = pow(rim, uDensityScaleHeight * 0.35);

  // Scattering phase angles
  float cosTheta = dot(viewDir, -lightDir);
  float rayleighScattering = rayleighPhase(cosTheta);
  float mieScattering = henyeyGreensteinPhase(cosTheta, uMieG) * uMieCoeff * 10.0;

  // Day/night terminator falloff
  float NdotL = max(dot(norm, lightDir), 0.0);
  float dayTerminator = smoothstep(-0.2, 0.4, dot(norm, lightDir));

  // Synthesize Rayleigh color dispersion with Mie halo
  vec3 rayleighColor = uRayleighCoeffs * 40.0 * rayleighScattering;
  vec3 mieColor = vec3(1.0, 0.95, 0.85) * mieScattering;

  vec3 finalAtmosphere = (rayleighColor + mieColor) * opticalDensity * (dayTerminator * 0.85 + 0.15);

  float alpha = clamp(opticalDensity * (0.6 + NdotL * 0.4), 0.0, 0.95);

  gl_FragColor = vec4(finalAtmosphere, alpha);

  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`

export function createAtmosphereMaterial(
  atmosphere: AtmosphereGenome
): THREE.ShaderMaterial {
  const [r, g, b] = atmosphere.rayleighCoefficients

  const uniforms: AtmosphereUniforms = {
    uRayleighCoeffs: { value: new THREE.Vector3(r, g, b) },
    uMieCoeff: { value: atmosphere.mieCoefficient },
    uMieG: { value: atmosphere.mieDirectionalG },
    uDensityScaleHeight: { value: atmosphere.densityScaleHeight },
    uSunDirection: { value: new THREE.Vector3(500, 200, 300).normalize() },
  }

  return new THREE.ShaderMaterial({
    uniforms,
    vertexShader: atmosphereVertexShader,
    fragmentShader: atmosphereFragmentShader,
    blending: THREE.AdditiveBlending,
    side: THREE.BackSide,
    transparent: true,
    depthWrite: false,
  })
}
