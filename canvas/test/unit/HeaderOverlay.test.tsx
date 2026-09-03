import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { HeaderOverlay } from '@/components/ui/HeaderOverlay'

describe('HeaderOverlay', () => {
  it('renders DevPlanet branding and username handle', () => {
    render(<HeaderOverlay />)

    expect(screen.getByText('DevPlanet')).toBeInTheDocument()
    expect(screen.getByText('Procedural World Engine')).toBeInTheDocument()
    expect(screen.getByText('@spandev')).toBeInTheDocument()
    expect(screen.getByText('Orbiting')).toBeInTheDocument()
  })
})
