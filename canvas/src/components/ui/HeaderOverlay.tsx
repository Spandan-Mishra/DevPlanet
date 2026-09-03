import { Sparkles } from 'lucide-react'
import { usePlanetStore } from '@/store/planetStore'

export function HeaderOverlay() {
  const username = usePlanetStore((state) => state.genome.meta.username)
  const autoRotate = usePlanetStore((state) => state.autoRotate)
  const toggleAutoRotate = usePlanetStore((state) => state.toggleAutoRotate)

  return (
    <header className="pointer-events-none absolute inset-x-0 top-0 z-20 flex items-center justify-between p-6 sm:p-8">
      {/* Top Left: DevPlanet Logo */}
      <div className="pointer-events-auto flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/10 text-xl backdrop-blur-md transition-transform hover:scale-105">
          🪐
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-wider text-white">
            DevPlanet
          </h1>
          <p className="text-xs font-medium tracking-wide text-zinc-400">
            Procedural World Engine
          </p>
        </div>
      </div>

      {/* Top Right: User GitHub Handle & Quick Controls */}
      <div className="pointer-events-auto flex items-center gap-3">
        <button
          onClick={toggleAutoRotate}
          title="Toggle Rotation"
          className="flex h-10 items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 text-xs font-semibold text-zinc-300 backdrop-blur-md transition-all hover:border-white/20 hover:bg-white/10"
        >
          <Sparkles className="h-3.5 w-3.5 text-cyan-400" />
          <span>{autoRotate ? 'Orbiting' : 'Paused'}</span>
        </button>

        <div className="flex h-10 items-center gap-2.5 rounded-xl border border-white/15 bg-black/60 px-4 backdrop-blur-md">
          <div className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs font-mono font-bold tracking-tight text-white">
            @{username}
          </span>
        </div>
      </div>
    </header>
  )
}
