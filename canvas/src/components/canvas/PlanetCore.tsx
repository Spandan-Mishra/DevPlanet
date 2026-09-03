import { useRef } from 'react'
import { useFrame, type ThreeEvent } from '@react-three/fiber'
import * as THREE from 'three'
import { usePlanetStore } from '@/store/planetStore'
import type { LandformNode } from '@/types/genome'

export function PlanetCore() {
  const planetGroupRef = useRef<THREE.Group>(null)
  const ringsRef = useRef<THREE.Mesh>(null)
  const moonsGroupRef = useRef<THREE.Group>(null)

  const genome = usePlanetStore((state) => state.genome)
  const autoRotate = usePlanetStore((state) => state.autoRotate)
  const setHoveredLandform = usePlanetStore((state) => state.setHoveredLandform)
  const setSelectedLandform = usePlanetStore((state) => state.setSelectedLandform)

  const { celestial, topology, surfaceMaterial } = genome

  // Convert unit norm S^2 plate centers to 3D surface coordinates (R = 100)
  const landformMarkers = topology.landforms.map((landform) => {
    const [nx, ny, nz] = landform.plateCenter
    const r = topology.baseRadius * (1.0 + landform.elevationFactor * 0.04)
    return {
      landform,
      position: [nx * r, ny * r, nz * r] as [number, number, number],
    }
  })

  // Animation frame: planet rotation, moon orbits, axial tilt
  useFrame((_, delta) => {
    if (planetGroupRef.current && autoRotate) {
      planetGroupRef.current.rotation.y += delta * celestial.rotationSpeed * 0.5
    }
    if (moonsGroupRef.current) {
      moonsGroupRef.current.rotation.y += delta * 0.15
    }
  })

  const handlePointerOver = (
    e: ThreeEvent<PointerEvent>,
    landform: LandformNode
  ) => {
    e.stopPropagation()
    // Calculate 2D screen coordinates
    const screenPos = { x: e.clientX, y: e.clientY }
    setHoveredLandform(landform, screenPos)
  }

  const handlePointerOut = (e: ThreeEvent<PointerEvent>) => {
    e.stopPropagation()
    setHoveredLandform(null)
  }

  const handleClick = (
    e: ThreeEvent<MouseEvent>,
    landform: LandformNode
  ) => {
    e.stopPropagation()
    setSelectedLandform(landform)
  }

  return (
    <group
      rotation={[0, 0, celestial.axialTilt]}
      position={[0, 0, 0]}
    >
      {/* 1. Main Rotating Planetary Body */}
      <group ref={planetGroupRef}>
        {/* Procedural Planet Mesh */}
        <mesh castShadow receiveShadow>
          <sphereGeometry args={[topology.baseRadius, 64, 64]} />
          <meshStandardMaterial
            color={surfaceMaterial.elevationColorRamp[2]?.hex || '#1a5276'}
            roughness={0.7}
            metalness={surfaceMaterial.metallicFactor}
          />
        </mesh>

        {/* Ocean Surface Layer */}
        <mesh>
          <sphereGeometry
            args={[topology.baseRadius * (0.99 + topology.seaLevel * 0.01), 48, 48]}
          />
          <meshStandardMaterial
            color={surfaceMaterial.elevationColorRamp[0]?.hex || '#0a192f'}
            roughness={0.15}
            metalness={0.8}
            transparent
            opacity={0.88}
          />
        </mesh>

        {/* Landform Repository Markers */}
        {landformMarkers.map(({ landform, position }) => (
          <group key={landform.repoName} position={position}>
            {/* Hit-box sphere for raycasting */}
            <mesh
              onPointerOver={(e) => handlePointerOver(e, landform)}
              onPointerOut={handlePointerOut}
              onClick={(e) => handleClick(e, landform)}
            >
              <sphereGeometry args={[6.5, 16, 16]} />
              <meshBasicMaterial
                color="#ffffff"
                wireframe
                transparent
                opacity={0.35}
              />
            </mesh>

            {/* Glowing Beacon Core */}
            <mesh>
              <sphereGeometry args={[2.2, 12, 12]} />
              <meshStandardMaterial
                color="#00ffcc"
                emissive="#00ffcc"
                emissiveIntensity={1.8}
              />
            </mesh>
          </group>
        ))}
      </group>

      {/* 2. Planetary Asteroid Rings */}
      {celestial.rings.enabled && (
        <mesh
          ref={ringsRef}
          rotation={[Math.PI / 2 + 0.1, 0, 0]}
          position={[0, 0, 0]}
        >
          <ringGeometry
            args={[
              celestial.rings.innerRadius,
              celestial.rings.outerRadius,
              64,
            ]}
          />
          <meshStandardMaterial
            color={celestial.rings.tint}
            side={THREE.DoubleSide}
            transparent
            opacity={celestial.rings.density * 0.75}
            roughness={0.8}
          />
        </mesh>
      )}

      {/* 3. Orbiting Keplerian Moons */}
      <group ref={moonsGroupRef}>
        {celestial.moons.map((moon) => (
          <group
            key={moon.id}
            rotation={[moon.inclination, 0, 0]}
          >
            <mesh position={[moon.orbitRadius, 0, 0]}>
              <sphereGeometry args={[moon.radius, 24, 24]} />
              <meshStandardMaterial
                color={moon.color}
                roughness={0.85}
                metalness={0.1}
              />
            </mesh>
          </group>
        ))}
      </group>
    </group>
  )
}
