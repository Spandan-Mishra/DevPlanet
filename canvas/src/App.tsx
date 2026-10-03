import { SceneViewport } from '@/components/canvas/SceneViewport'
import { HeaderOverlay } from '@/components/ui/HeaderOverlay'
import { RepoDetailModal } from '@/components/ui/RepoDetailModal'
import { RepoHoverTooltip } from '@/components/ui/RepoHoverTooltip'

export function App() {
  return (
    <main className="relative h-screen w-screen overflow-hidden bg-[#030308]">
      {/* Top Branding & Handle Overlay */}
      <HeaderOverlay />

      {/* 3D WebGL Canvas Scene Viewport */}
      <SceneViewport />

      {/* High-Contrast White Legend Tooltip Bubble */}
      <RepoHoverTooltip />

      {/* Interactive Landform Click Glimpse Modal */}
      <RepoDetailModal />
    </main>
  )
}

export default App
