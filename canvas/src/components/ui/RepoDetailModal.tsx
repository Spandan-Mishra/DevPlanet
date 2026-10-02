import { useEffect } from 'react'
import {
  CircleDot,
  ExternalLink,
  GitCommit,
  GitFork,
  Layers,
  Star,
  X,
} from 'lucide-react'
import { usePlanetStore } from '@/store/planetStore'

export function RepoDetailModal() {
  const selectedLandform = usePlanetStore((state) => state.selectedLandform)
  const closeSelectedLandform = usePlanetStore(
    (state) => state.closeSelectedLandform
  )
  const repoStats = usePlanetStore((state) => state.repoStats)
  const username = usePlanetStore((state) => state.genome.meta.username)

  // Listen for Escape key to close modal
  useEffect(() => {
    if (!selectedLandform) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        closeSelectedLandform()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => {
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [selectedLandform, closeSelectedLandform])

  if (!selectedLandform) {
    return null
  }

  const stat = repoStats[selectedLandform.repoName] || {
    name: selectedLandform.repoName,
    description: 'Repository Landform Geological Mass',
    stars: Math.round(selectedLandform.elevationFactor * 250),
    forks: Math.round(selectedLandform.roughness * 80),
    commitCount: Math.round(selectedLandform.plateRadius * 600),
    openIssues: 0,
    primaryLanguage: null,
    url: `https://github.com/${username}/${selectedLandform.repoName}`,
  }

  const githubUrl =
    stat.url || `https://github.com/${username}/${selectedLandform.repoName}`

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label={`Repository Details - ${stat.name}`}
      onClick={closeSelectedLandform}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-xs transition-opacity duration-150 animate-in fade-in"
    >
      {/* Modal Card (click inside does not trigger backdrop close) */}
      <div
        onClick={(e) => e.stopPropagation()}
        className="relative w-full max-w-lg border-2 border-black bg-white p-5 text-black shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] transition-all animate-in zoom-in-95 sm:p-6"
      >
        {/* Top Bar: Sector Tag + Close Button */}
        <div className="flex items-center justify-between border-b-2 border-black/15 pb-3">
          <div className="flex items-center gap-2">
            <span
              className="border border-black bg-zinc-100 px-2 py-0.5 font-mono text-[11px] font-bold uppercase tracking-wider text-zinc-800"
            >
              🚀 Sector Landform
            </span>
            <span className="font-mono text-xs font-semibold text-zinc-500">
              #{selectedLandform.repoName.slice(0, 6)}
            </span>
          </div>

          <button
            type="button"
            onClick={closeSelectedLandform}
            aria-label="Close modal"
            className="flex h-8 w-8 items-center justify-center border-2 border-black bg-zinc-100 text-black transition-colors hover:bg-black hover:text-white"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Repository Title & Language Badge */}
        <div className="mt-4 flex flex-wrap items-start justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="text-2xl" role="img" aria-label="satellite">
              🛰️
            </span>
            <h2 className="font-mono text-xl font-black tracking-tight text-black sm:text-2xl">
              {stat.name}
            </h2>
          </div>

          {/* Primary Language Badge */}
          <div className="flex items-center gap-1.5 border border-black/20 bg-zinc-50 px-2.5 py-1 text-xs">
            <span
              className="h-2.5 w-2.5 rounded-full border border-black/30"
              style={{
                backgroundColor: stat.primaryLanguage?.color || '#71717a',
              }}
            />
            <span className="font-mono font-bold text-zinc-900">
              {stat.primaryLanguage?.name || 'Unknown'}
            </span>
          </div>
        </div>

        {/* Description / Sector Summary */}
        <p className="mt-3 text-sm leading-relaxed text-zinc-700">
          {stat.description ||
            'Algorithmic surface elevation formed by Git commit activity and repository topology.'}
        </p>

        {/* Geological Sector Profile */}
        <div className="mt-3.5 flex flex-wrap items-center gap-2 border border-black/10 bg-zinc-50 p-2.5 text-xs text-zinc-600">
          <Layers className="h-3.5 w-3.5 text-zinc-800" />
          <span className="font-mono">
            Radius: <strong>{(selectedLandform.plateRadius * 100).toFixed(0)}%</strong>
          </span>
          <span className="text-zinc-300">•</span>
          <span className="font-mono">
            Elevation: <strong>{selectedLandform.elevationFactor.toFixed(2)}x</strong>
          </span>
          <span className="text-zinc-300">•</span>
          <span className="font-mono">
            Roughness: <strong>{selectedLandform.roughness.toFixed(2)}</strong>
          </span>
        </div>

        {/* Metric Grid: Commits, Stars, Forks, Open Issues */}
        <div className="mt-4 grid grid-cols-2 gap-2 border-2 border-black bg-zinc-50 p-3 sm:grid-cols-4 sm:gap-3">
          {/* Commits */}
          <div className="flex flex-col items-center justify-center border border-black/15 bg-white p-2 text-center">
            <div className="flex items-center gap-1 text-[11px] font-bold text-zinc-600">
              <GitCommit className="h-3.5 w-3.5 text-black" />
              <span>Commits</span>
            </div>
            <span className="mt-0.5 font-mono text-sm font-black text-black sm:text-base">
              {stat.commitCount.toLocaleString()}
            </span>
          </div>

          {/* Stars */}
          <div className="flex flex-col items-center justify-center border border-black/15 bg-white p-2 text-center">
            <div className="flex items-center gap-1 text-[11px] font-bold text-amber-700">
              <Star className="h-3.5 w-3.5 fill-amber-500 text-amber-500" />
              <span>Stars</span>
            </div>
            <span className="mt-0.5 font-mono text-sm font-black text-black sm:text-base">
              {stat.stars.toLocaleString()}
            </span>
          </div>

          {/* Forks */}
          <div className="flex flex-col items-center justify-center border border-black/15 bg-white p-2 text-center">
            <div className="flex items-center gap-1 text-[11px] font-bold text-zinc-600">
              <GitFork className="h-3.5 w-3.5 text-black" />
              <span>Forks</span>
            </div>
            <span className="mt-0.5 font-mono text-sm font-black text-black sm:text-base">
              {stat.forks.toLocaleString()}
            </span>
          </div>

          {/* Open Issues */}
          <div className="flex flex-col items-center justify-center border border-black/15 bg-white p-2 text-center">
            <div className="flex items-center gap-1 text-[11px] font-bold text-emerald-700">
              <CircleDot className="h-3.5 w-3.5 text-emerald-600" />
              <span>Issues</span>
            </div>
            <span className="mt-0.5 font-mono text-sm font-black text-black sm:text-base">
              {(stat.openIssues ?? 0).toLocaleString()}
            </span>
          </div>
        </div>

        {/* Footer Quick Action: Direct View on GitHub */}
        <div className="mt-5 flex items-center justify-end gap-3 border-t-2 border-black/15 pt-4">
          <button
            type="button"
            onClick={closeSelectedLandform}
            className="border-2 border-transparent px-3 py-2 font-mono text-xs font-bold text-zinc-600 transition-colors hover:text-black"
          >
            Dismiss
          </button>

          <a
            href={githubUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 border-2 border-black bg-black px-4 py-2 font-mono text-xs font-black text-white shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] transition-transform hover:-translate-x-0.5 hover:-translate-y-0.5 active:translate-x-0.5 active:translate-y-0.5 active:shadow-none"
          >
            <span>View on GitHub</span>
            <ExternalLink className="h-3.5 w-3.5" />
          </a>
        </div>
      </div>
    </div>
  )
}
