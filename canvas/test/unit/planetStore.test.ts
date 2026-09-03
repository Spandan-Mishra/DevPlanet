import { describe, expect, it } from 'vitest'
import { mockPlanetGenome } from '@/data/mockGenome'
import { usePlanetStore } from '@/store/planetStore'

describe('usePlanetStore', () => {
  it('initializes with default mock genome', () => {
    const state = usePlanetStore.getState()
    expect(state.genome.meta.username).toBe('spandev')
    expect(state.genome.celestial.radius).toBe(100.0)
    expect(state.hoveredLandform).toBeNull()
    expect(state.autoRotate).toBe(true)
  })

  it('updates hovered landform and screen position', () => {
    const { setHoveredLandform } = usePlanetStore.getState()
    const targetLandform = mockPlanetGenome.topology.landforms[0]

    setHoveredLandform(targetLandform, { x: 250, y: 180 })

    const updated = usePlanetStore.getState()
    expect(updated.hoveredLandform?.repoName).toBe('DevPlanet')
    expect(updated.hoverPosition2D).toEqual({ x: 250, y: 180 })

    // Clear hover
    setHoveredLandform(null)
    expect(usePlanetStore.getState().hoveredLandform).toBeNull()
  })

  it('toggles autoRotate flag', () => {
    const { toggleAutoRotate } = usePlanetStore.getState()
    const initial = usePlanetStore.getState().autoRotate

    toggleAutoRotate()
    expect(usePlanetStore.getState().autoRotate).toBe(!initial)
  })
})
