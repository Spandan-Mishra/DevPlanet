import * as THREE from 'three'
import { describe, expect, it } from 'vitest'
import { mockPlanetGenome } from '@/data/mockGenome'
import { createTerrainMaterial } from '@/shaders/terrainShader'

describe('createTerrainMaterial', () => {
  it('instantiates Three.js ShaderMaterial with genome uniforms', () => {
    const material = createTerrainMaterial(
      mockPlanetGenome.topology,
      mockPlanetGenome.surfaceMaterial
    )

    expect(material).toBeInstanceOf(THREE.ShaderMaterial)
    expect(material.uniforms.uBaseRadius.value).toBe(100.0)
    expect(material.uniforms.uSeaLevel.value).toBe(0.45)
    expect(material.uniforms.uOctaves.value).toBe(6)
    expect(material.uniforms.uLandformCount.value).toBe(3)
    expect(material.uniforms.uElevationRamp.value.length).toBe(6)
  })
})
