import { render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it } from 'vitest'
import { RepoHoverTooltip } from '@/components/ui/RepoHoverTooltip'
import { mockPlanetGenome } from '@/data/mockGenome'
import { usePlanetStore } from '@/store/planetStore'

describe('RepoHoverTooltip', () => {
  beforeEach(() => {
    usePlanetStore.setState({
      hoveredLandform: null,
      hoverPosition2D: null,
    })
  })

  it('renders nothing when no landform is hovered', () => {
    const { container } = render(<RepoHoverTooltip />)
    expect(container.firstChild).toBeNull()
  })

  it('renders crisp white tooltip with repo metrics when landform is hovered', () => {
    const landform = mockPlanetGenome.topology.landforms[0]
    usePlanetStore.setState({
      hoveredLandform: landform,
      hoverPosition2D: { x: 300, y: 200 },
    })

    render(<RepoHoverTooltip />)

    expect(screen.getByText('DevPlanet')).toBeInTheDocument()
    expect(screen.getByText('Commits')).toBeInTheDocument()
    expect(screen.getByText('580')).toBeInTheDocument()
    expect(screen.getByText('Stars')).toBeInTheDocument()
    expect(screen.getByText('1,250')).toBeInTheDocument()
    expect(screen.getByText('Forks')).toBeInTheDocument()
    expect(screen.getByText('340')).toBeInTheDocument()
    expect(screen.getByText('Rust')).toBeInTheDocument()
  })
})
