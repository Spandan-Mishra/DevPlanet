import { Suspense } from 'react'
import { OrbitControls } from '@react-three/drei'
import { Canvas } from '@react-three/fiber'
import * as THREE from 'three'
import { CosmicBackground } from './CosmicBackground'
import { PlanetCore } from './PlanetCore'

export function SceneViewport() {
  return (
    <div className="relative h-full w-full overflow-hidden bg-[#030308]">
      <Canvas
        camera={{
          position: [0, 60, 320],
          fov: 45,
          near: 1.0,
          far: 4000.0,
        }}
        gl={{
          antialias: true,
          toneMapping: THREE.ACESFilmicToneMapping,
          toneMappingExposure: 1.2,
          powerPreference: 'high-performance',
        }}
        dpr={[1, 2]}
      >
        <Suspense fallback={null}>
          {/* Universal Cosmic Star Simulation Background */}
          <CosmicBackground />

          {/* Celestial Illumination */}
          <ambientLight intensity={0.25} color="#d4e6f1" />
          <directionalLight
            position={[500, 200, 300]}
            intensity={2.8}
            color="#ffffff"
            castShadow
          />
          <pointLight
            position={[-300, -100, -200]}
            intensity={0.6}
            color="#81ecec"
          />

          {/* Centered Planet & Orbital Systems */}
          <PlanetCore />

          {/* 360-Degree Orbital Controls (Pan, Rotate & Zoom) */}
          <OrbitControls
            enableDamping
            dampingFactor={0.06}
            rotateSpeed={0.6}
            panSpeed={0.8}
            zoomSpeed={0.9}
            minDistance={125.0} // Near surface view
            maxDistance={850.0} // Macro cosmic view
            enablePan={true}
          />
        </Suspense>
      </Canvas>
    </div>
  )
}
