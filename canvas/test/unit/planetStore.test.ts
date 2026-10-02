import { describe, expect, it } from 'vitest'
import { mockPlanetGenome } from '@/data/mockGenome'
import { usePlanetStore } from '@/store/planetStore'

describe('usePlanetStore', () => {
  it('initializes with default mock genome and repo stats', () => {
    const state = usePlanetStore.getState()
    expect(state.genome.meta.username).toBe('spandev')
    expect(state.genome.celestial.radius).toBe(100.0)
    expect(state.hoveredLandform).toBeNull()
    expect(state.selectedLandform).toBeNull()
    expect(state.autoRotate).toBe(true)
    expect(state.repoStats.DevPlanet?.openIssues).toBe(12)
    expect(state.repoStats.DevPlanet?.url).toBe('https://github.com/spandev/DevPlanet')
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

  it('manages selected landform and modal close action', () => {
    const { setSelectedLandform, closeSelectedLandform } = usePlanetStore.getState()
    const targetLandform = mockPlanetGenome.topology.landforms[1]

    setSelectedLandform(targetLandform)
    expect(usePlanetStore.getState().selectedLandform?.repoName).toBe('forge-engine')

    closeSelectedLandform()
    expect(usePlanetStore.getState().selectedLandform).toBeNull()
  })

  it('toggles autoRotate flag', () => {
    const { toggleAutoRotate } = usePlanetStore.getState()
    const initial = usePlanetStore.getState().autoRotate

    toggleAutoRotate()
    expect(usePlanetStore.getState().autoRotate).toBe(!initial)
  })
})
