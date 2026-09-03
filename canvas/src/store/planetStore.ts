import { create } from 'zustand'
import { mockPlanetGenome } from '@/data/mockGenome'
import type { LandformNode, LandformRepoStat, PlanetGenome } from '@/types/genome'

interface PlanetState {
  genome: PlanetGenome
  hoveredLandform: LandformNode | null
  selectedLandform: LandformNode | null
  hoverPosition2D: { x: number; y: number } | null
  repoStats: Record<string, LandformRepoStat>
  isLoading: boolean
  autoRotate: boolean

  // Actions
  setGenome: (genome: PlanetGenome) => void
  setHoveredLandform: (
    landform: LandformNode | null,
    screenPos?: { x: number; y: number } | null
  ) => void
  setSelectedLandform: (landform: LandformNode | null) => void
  setRepoStats: (stats: Record<string, LandformRepoStat>) => void
  setIsLoading: (loading: boolean) => void
  toggleAutoRotate: () => void
}

export const usePlanetStore = create<PlanetState>((set) => ({
  genome: mockPlanetGenome,
  hoveredLandform: null,
  selectedLandform: null,
  hoverPosition2D: null,
  repoStats: {
    DevPlanet: {
      name: 'DevPlanet',
      description: 'Procedural 3D planetary visualization of GitHub profiles',
      stars: 1250,
      forks: 340,
      commitCount: 580,
      primaryLanguage: { name: 'Rust', color: '#dea584' },
    },
    'forge-engine': {
      name: 'forge-engine',
      description: 'Algorithmic procedural seed & climate synthesizer',
      stars: 480,
      forks: 110,
      commitCount: 290,
      primaryLanguage: { name: 'Python', color: '#3572A5' },
    },
    'canvas-renderer': {
      name: 'canvas-renderer',
      description: 'React Three Fiber WebGL shaders and boids simulation',
      stars: 620,
      forks: 150,
      commitCount: 340,
      primaryLanguage: { name: 'TypeScript', color: '#3178C6' },
    },
  },
  isLoading: false,
  autoRotate: true,

  setGenome: (genome) => set({ genome }),
  setHoveredLandform: (landform, screenPos = null) =>
    set({
      hoveredLandform: landform,
      hoverPosition2D: screenPos,
    }),
  setSelectedLandform: (landform) => set({ selectedLandform: landform }),
  setRepoStats: (stats) => set({ repoStats: stats }),
  setIsLoading: (isLoading) => set({ isLoading }),
  toggleAutoRotate: () => set((state) => ({ autoRotate: !state.autoRotate })),
}))
