import { describe, expect, it } from 'vitest'
import { KeplerianMoons } from '@/components/canvas/KeplerianMoons'
import { mockPlanetGenome } from '@/data/mockGenome'

describe('KeplerianMoons', () => {
  it('exports valid component definition for moons', () => {
    expect(KeplerianMoons).toBeDefined()
    expect(mockPlanetGenome.celestial.moons.length).toBe(2)
  })
})
