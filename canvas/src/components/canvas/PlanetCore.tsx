import { useEffect, useMemo, useRef } from 'react'
import { useFrame, type ThreeEvent } from '@react-three/fiber'
import * as THREE from 'three'
import { AsteroidRings } from '@/components/canvas/AsteroidRings'
import { KeplerianMoons } from '@/components/canvas/KeplerianMoons'
import { createAtmosphereMaterial } from '@/shaders/atmosphereShader'
import { createTerrainMaterial } from '@/shaders/terrainShader'
import { usePlanetStore } from '@/store/planetStore'
import type { LandformNode } from '@/types/genome'

export function PlanetCore() {
  const planetGroupRef = useRef<THREE.Group>(null)

  const genome = usePlanetStore((state) => state.genome)
  const autoRotate = usePlanetStore((state) => state.autoRotate)
  const setHoveredLandform = usePlanetStore((state) => state.setHoveredLandform)
  const setSelectedLandform = usePlanetStore((state) => state.setSelectedLandform)

  const { celestial, topology, surfaceMaterial, atmosphere } = genome

  // Memoize custom GPU procedural terrain ShaderMaterial
  const terrainMaterial = useMemo(
    () => createTerrainMaterial(topology, surfaceMaterial),
    [topology, surfaceMaterial]
  )

  // Dispose previous terrain shader material on dependency change or unmount
  useEffect(() => {
    return () => {
      terrainMaterial.dispose()
    }
  }, [terrainMaterial])

  // Memoize custom Rayleigh/Mie atmospheric rim glow ShaderMaterial
  const atmosphereMaterial = useMemo(
    () => (atmosphere.hasAtmosphere ? createAtmosphereMaterial(atmosphere) : null),
    [atmosphere]
  )

  // Dispose previous atmosphere shader material on change or unmount
  useEffect(() => {
    return () => {
      atmosphereMaterial?.dispose()
    }
  }, [atmosphereMaterial])

  // Convert unit norm S^2 plate centers to 3D surface coordinates (R = 100 + elevation)
  const landformMarkers = useMemo(() => {
    return topology.landforms.map((landform) => {
      const [nx, ny, nz] = landform.plateCenter
      const elevationOffset =
        topology.maxAltitude * Math.min(1.0, landform.elevationFactor * 0.4)
      const r = topology.baseRadius + elevationOffset
      return {
        landform,
        position: [nx * r, ny * r, nz * r] as [number, number, number],
      }
    })
  }, [topology])

  // Animation frame: planet rotation around axial tilt
  useFrame((_, delta) => {
    if (planetGroupRef.current && autoRotate) {
      planetGroupRef.current.rotation.y += delta * celestial.rotationSpeed * 0.5
    }
  })

  const handlePointerOver = (
    e: ThreeEvent<PointerEvent>,
    landform: LandformNode
  ) => {
    e.stopPropagation()
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
        {/* Procedural GPU Terrain Mesh with FBM Elevation Displacement */}
        <mesh
          castShadow
          receiveShadow
          material={terrainMaterial}
        >
          <icosahedronGeometry args={[topology.baseRadius, 24]} />
        </mesh>

        {/* Ocean Surface Layer */}
        <mesh>
          <sphereGeometry
            args={[
              topology.baseRadius * (1.002 + topology.seaLevel * 0.015),
              64,
              64,
            ]}
          />
          <meshStandardMaterial
            color={surfaceMaterial.elevationColorRamp[0]?.hex || '#0a192f'}
            roughness={0.12}
            metalness={0.85}
            transparent
            opacity={0.88}
          />
        </mesh>

        {/* Rayleigh & Mie Atmospheric Halo Glow Shell */}
        {atmosphere.hasAtmosphere && atmosphereMaterial && (
          <mesh material={atmosphereMaterial}>
            <sphereGeometry
              args={[topology.baseRadius * 1.15, 64, 64]}
            />
          </mesh>
        )}

        {/* Landform Repository Markers */}
        {landformMarkers.map(({ landform, position }) => (
          <group key={landform.repoName} position={position}>
            {/* Hit-box sphere for raycasting */}
            <mesh
              onPointerOver={(e) => handlePointerOver(e, landform)}
              onPointerOut={handlePointerOut}
              onClick={(e) => handleClick(e, landform)}
            >
              <sphereGeometry args={[7.0, 16, 16]} />
              <meshBasicMaterial
                color="#ffffff"
                wireframe
                transparent
                opacity={0.3}
              />
            </mesh>

            {/* Glowing Beacon Core */}
            <mesh>
              <sphereGeometry args={[2.5, 12, 12]} />
              <meshStandardMaterial
                color="#00ffcc"
                emissive="#00ffcc"
                emissiveIntensity={2.0}
              />
            </mesh>
          </group>
        ))}
      </group>

      {/* 2. Instanced Planetary Asteroid Dust Rings */}
      {celestial.rings.enabled && (
        <AsteroidRings rings={celestial.rings} />
      )}

      {/* 3. Orbiting Keplerian Moons with Orbital Traces */}
      <KeplerianMoons moons={celestial.moons} />
    </group>
  )
}
