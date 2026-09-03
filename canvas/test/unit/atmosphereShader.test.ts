import * as THREE from 'three'
import { describe, expect, it } from 'vitest'
import { mockPlanetGenome } from '@/data/mockGenome'
import { createAtmosphereMaterial } from '@/shaders/atmosphereShader'

describe('createAtmosphereMaterial', () => {
  it('instantiates Three.js ShaderMaterial with Rayleigh and Mie optical coefficients', () => {
    const material = createAtmosphereMaterial(mockPlanetGenome.atmosphere)

    expect(material).toBeInstanceOf(THREE.ShaderMaterial)
    expect(material.transparent).toBe(true)
    expect(material.blending).toBe(THREE.AdditiveBlending)
    expect(material.side).toBe(THREE.BackSide)

    const rayleigh = material.uniforms.uRayleighCoeffs.value as THREE.Vector3
    expect(rayleigh.x).toBeCloseTo(0.0072)
    expect(rayleigh.y).toBeCloseTo(0.0145)
    expect(rayleigh.z).toBeCloseTo(0.0385)
    expect(material.uniforms.uDensityScaleHeight.value).toBe(9.8)
  })
})
