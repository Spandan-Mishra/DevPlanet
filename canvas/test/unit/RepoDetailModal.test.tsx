import { fireEvent, render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it } from 'vitest'
import { RepoDetailModal } from '@/components/ui/RepoDetailModal'
import { mockPlanetGenome } from '@/data/mockGenome'
import { usePlanetStore } from '@/store/planetStore'

describe('RepoDetailModal', () => {
  beforeEach(() => {
    usePlanetStore.setState({
      selectedLandform: null,
    })
  })

  it('renders nothing when selectedLandform is null', () => {
    const { container } = render(<RepoDetailModal />)
    expect(container.firstChild).toBeNull()
  })

  it('renders crisp glimpse card with metrics and external GitHub link when landform is selected', () => {
    const landform = mockPlanetGenome.topology.landforms[0]!
    usePlanetStore.setState({
      selectedLandform: landform,
    })

    render(<RepoDetailModal />)

    // Header & Title
    expect(screen.getByRole('dialog')).toBeInTheDocument()
    expect(screen.getByText('DevPlanet')).toBeInTheDocument()
    expect(screen.getByText('Rust')).toBeInTheDocument()

    // Metric Grid
    expect(screen.getByText('Commits')).toBeInTheDocument()
    expect(screen.getByText('580')).toBeInTheDocument()
    expect(screen.getByText('Stars')).toBeInTheDocument()
    expect(screen.getByText('1,250')).toBeInTheDocument()
    expect(screen.getByText('Forks')).toBeInTheDocument()
    expect(screen.getByText('340')).toBeInTheDocument()
    expect(screen.getByText('Issues')).toBeInTheDocument()
    expect(screen.getByText('12')).toBeInTheDocument()

    // External Link Button
    const githubLink = screen.getByRole('link', { name: /view on github/i })
    expect(githubLink).toHaveAttribute('href', 'https://github.com/spandev/DevPlanet')
    expect(githubLink).toHaveAttribute('target', '_blank')
    expect(githubLink).toHaveAttribute('rel', 'noopener noreferrer')
  })

  it('renders "Unknown" for primary language when landform has no predefined stats', () => {
    const unlistedLandform = {
      repoName: 'unlisted-repo',
      plateCenter: [0.1, 0.2, 0.9] as [number, number, number],
      plateRadius: 0.2,
      elevationFactor: 1.1,
      roughness: 0.4,
    }
    usePlanetStore.setState({
      selectedLandform: unlistedLandform,
    })

    render(<RepoDetailModal />)

    expect(screen.getByText('unlisted-repo')).toBeInTheDocument()
    expect(screen.getByText('Unknown')).toBeInTheDocument()
  })

  it('closes modal when the close button is clicked', () => {
    const landform = mockPlanetGenome.topology.landforms[0]!
    usePlanetStore.setState({
      selectedLandform: landform,
    })

    render(<RepoDetailModal />)

    const closeBtn = screen.getByRole('button', { name: /close modal/i })
    fireEvent.click(closeBtn)

    expect(usePlanetStore.getState().selectedLandform).toBeNull()
  })

  it('closes modal when backdrop is clicked, but not when card is clicked', () => {
    const landform = mockPlanetGenome.topology.landforms[0]!
    usePlanetStore.setState({
      selectedLandform: landform,
    })

    render(<RepoDetailModal />)

    const dialogBackdrop = screen.getByRole('dialog')

    // Clicking card inside shouldn't close modal
    const titleElement = screen.getByText('DevPlanet')
    fireEvent.click(titleElement)
    expect(usePlanetStore.getState().selectedLandform).not.toBeNull()

    // Clicking backdrop should close modal
    fireEvent.click(dialogBackdrop)
    expect(usePlanetStore.getState().selectedLandform).toBeNull()
  })

  it('closes modal when Escape key is pressed', () => {
    const landform = mockPlanetGenome.topology.landforms[0]!
    usePlanetStore.setState({
      selectedLandform: landform,
    })

    render(<RepoDetailModal />)

    expect(usePlanetStore.getState().selectedLandform).not.toBeNull()

    fireEvent.keyDown(window, { key: 'Escape' })

    expect(usePlanetStore.getState().selectedLandform).toBeNull()
  })

  it('traps Tab navigation within the modal card', () => {
    const landform = mockPlanetGenome.topology.landforms[0]!
    usePlanetStore.setState({
      selectedLandform: landform,
    })

    render(<RepoDetailModal />)

    const closeBtn = screen.getByRole('button', { name: /close modal/i })
    const githubLink = screen.getByRole('link', { name: /view on github/i })

    // Focus last element (View on GitHub link)
    githubLink.focus()
    expect(document.activeElement).toBe(githubLink)

    // Press Tab on last element -> wraps to first focusable element (close button)
    fireEvent.keyDown(window, { key: 'Tab' })
    expect(document.activeElement).toBe(closeBtn)

    // Press Shift+Tab on first element -> wraps back to last focusable element
    fireEvent.keyDown(window, { key: 'Tab', shiftKey: true })
    expect(document.activeElement).toBe(githubLink)
  })

  it('restores focus to previously active element upon modal close', () => {
    const triggerButton = document.createElement('button')
    triggerButton.textContent = 'Trigger'
    document.body.appendChild(triggerButton)
    triggerButton.focus()
    expect(document.activeElement).toBe(triggerButton)

    const landform = mockPlanetGenome.topology.landforms[0]!
    usePlanetStore.setState({
      selectedLandform: landform,
    })

    const { unmount } = render(<RepoDetailModal />)

    // Close modal
    unmount()
    expect(document.activeElement).toBe(triggerButton)
    document.body.removeChild(triggerButton)
  })
})
