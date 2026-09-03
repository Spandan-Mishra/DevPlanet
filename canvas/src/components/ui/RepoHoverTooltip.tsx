import { GitCommit, GitFork, Star } from 'lucide-react'
import { usePlanetStore } from '@/store/planetStore'

export function RepoHoverTooltip() {
  const hoveredLandform = usePlanetStore((state) => state.hoveredLandform)
  const hoverPosition2D = usePlanetStore((state) => state.hoverPosition2D)
  const repoStats = usePlanetStore((state) => state.repoStats)

  if (!hoveredLandform || !hoverPosition2D) {
    return null
  }

  const stat = repoStats[hoveredLandform.repoName] || {
    name: hoveredLandform.repoName,
    description: 'Repository Landform Mass',
    stars: Math.round(hoveredLandform.elevationFactor * 250),
    forks: Math.round(hoveredLandform.roughness * 80),
    commitCount: Math.round(hoveredLandform.plateRadius * 600),
    primaryLanguage: { name: 'Rust', color: '#dea584' },
  }

  // Offset tooltip slightly above and right of pointer
  const tooltipStyle: React.CSSProperties = {
    left: `${Math.min(hoverPosition2D.x + 16, window.innerWidth - 280)}px`,
    top: `${Math.max(hoverPosition2D.y - 120, 20)}px`,
  }

  return (
    <aside
      aria-label="Repository Landform Info"
      style={tooltipStyle}
      className="pointer-events-none fixed z-30 w-64 border-2 border-black bg-white p-3.5 text-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-all duration-75 animate-in fade-in zoom-in-95"
    >
      {/* Header: Space Icon + Repo Name */}
      <div className="flex items-center justify-between border-b border-black/15 pb-2">
        <div className="flex items-center gap-1.5 truncate">
          <span className="text-base" role="img" aria-label="satellite">
            🛰️
          </span>
          <span className="truncate font-mono text-sm font-black tracking-tight text-black">
            {stat.name}
          </span>
        </div>
        <span className="text-xs font-mono font-bold text-zinc-600">
          ✦ #{hoveredLandform.repoName.slice(0, 4)}
        </span>
      </div>

      {/* Description */}
      {stat.description && (
        <p className="mt-1.5 line-clamp-2 text-xs leading-snug text-zinc-700">
          {stat.description}
        </p>
      )}

      {/* Metrics Row: Commits, Stars, Forks */}
      <div className="mt-3 grid grid-cols-3 gap-1 border-t border-black/10 pt-2 text-center">
        {/* Commits */}
        <div className="flex flex-col items-center">
          <div className="flex items-center gap-1 text-[11px] font-bold text-zinc-600">
            <GitCommit className="h-3 w-3 text-black" />
            <span>Commits</span>
          </div>
          <span className="font-mono text-xs font-black text-black">
            {stat.commitCount.toLocaleString()}
          </span>
        </div>

        {/* Stars */}
        <div className="flex flex-col items-center border-x border-black/10 px-1">
          <div className="flex items-center gap-1 text-[11px] font-bold text-amber-600">
            <Star className="h-3 w-3 fill-amber-500 text-amber-500" />
            <span>Stars</span>
          </div>
          <span className="font-mono text-xs font-black text-black">
            {stat.stars.toLocaleString()}
          </span>
        </div>

        {/* Forks */}
        <div className="flex flex-col items-center">
          <div className="flex items-center gap-1 text-[11px] font-bold text-zinc-600">
            <GitFork className="h-3 w-3 text-black" />
            <span>Forks</span>
          </div>
          <span className="font-mono text-xs font-black text-black">
            {stat.forks.toLocaleString()}
          </span>
        </div>
      </div>

      {/* Footer: Language Badge + Space Glyph */}
      <div className="mt-2.5 flex items-center justify-between border-t border-black/10 pt-1.5 text-[11px]">
        <div className="flex items-center gap-1.5">
          <span
            className="h-2 w-2 rounded-full border border-black/30"
            style={{ backgroundColor: stat.primaryLanguage?.color || '#333' }}
          />
          <span className="font-mono font-semibold text-black">
            {stat.primaryLanguage?.name || 'Markdown'}
          </span>
        </div>
        <span className="font-mono text-[10px] text-zinc-500">
          🚀 Landform Sector
        </span>
      </div>
    </aside>
  )
}
