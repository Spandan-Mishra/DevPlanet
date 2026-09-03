import { SceneViewport } from '@/components/canvas/SceneViewport'
import { HeaderOverlay } from '@/components/ui/HeaderOverlay'
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
    </main>
  )
}

export default App
