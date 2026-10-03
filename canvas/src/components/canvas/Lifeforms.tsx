import { useEffect, useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { usePlanetStore } from '@/store/planetStore'
import type { InhabitantSpecies, LandformNode } from '@/types/genome'
import {
  isLodActive,
  isSectorInProximity,
  LOD_DISTANCE_THRESHOLD,
  SECTOR_PROXIMITY_THRESHOLD,
} from '@/utils/boidsLod'

// Scratch vectors and matrices to prevent memory allocations during useFrame
const _dummy = new THREE.Object3D()
const _scratchCamPos = new THREE.Vector3()
const _scratchLandformWorld = new THREE.Vector3()
const _tangentU = new THREE.Vector3()
const _tangentV = new THREE.Vector3()
const _boidPos = new THREE.Vector3()
const _forward = new THREE.Vector3()

interface BoidAgent {
  speciesType: string
  landformIndex: number
  orbitRadius: number
  orbitSpeed: number
  baseAltitude: number
  phaseOffset: number
  verticalFreq: number
  wobbleFreq: number
}

interface LandformLocalItem {
  landform: LandformNode
  localPos: THREE.Vector3
  centerUnit: THREE.Vector3
  elevationOffset: number
}

interface SpeciesMeshUnitProps {
  species: InhabitantSpecies
  meshRef: (mesh: THREE.InstancedMesh | null) => void
}

function SpeciesMeshUnit({ species, meshRef }: SpeciesMeshUnitProps) {
  const maxCount = species.population || 40

  const geometry = useMemo(() => {
    let geo: THREE.BufferGeometry
    if (species.type === 'avian_glider') {
      geo = new THREE.ConeGeometry(species.scale * 0.75, species.scale * 2.2, 4)
      geo.rotateX(Math.PI / 2)
    } else if (species.type === 'pelagic_swimmer') {
      geo = new THREE.CylinderGeometry(
        species.scale * 1.3,
        species.scale * 0.4,
        species.scale * 0.3,
        4
      )
    } else {
      geo = new THREE.SphereGeometry(species.scale * 0.7, 10, 10)
    }
    return geo
  }, [species.type, species.scale])

  const material = useMemo(() => {
    return new THREE.MeshStandardMaterial({
      color: species.bioluminescenceColor,
      emissive: species.bioluminescenceColor,
      emissiveIntensity: 2.2,
      roughness: 0.25,
      metalness: 0.1,
    })
  }, [species.bioluminescenceColor])

  useEffect(() => {
    return () => {
      geometry.dispose()
      material.dispose()
    }
  }, [geometry, material])

  return (
    <instancedMesh
      ref={meshRef}
      args={[geometry, material, maxCount]}
      frustumCulled={false}
      name={`lifeforms-${species.type}`}
    />
  )
}

export function Lifeforms() {
  const genome = usePlanetStore((state) => state.genome)
  const groupRef = useRef<THREE.Group>(null)
  const meshesRef = useRef<Record<string, THREE.InstancedMesh>>({})

  const { ecosystem, topology } = genome
  const { species } = ecosystem
  const { landforms, baseRadius, maxAltitude, seaLevel } = topology

  // Precompute landform local positions
  const landformLocalPositions = useMemo<LandformLocalItem[]>(() => {
    return landforms.map((landform) => {
      const [nx, ny, nz] = landform.plateCenter
      const elevationOffset =
        maxAltitude * Math.min(1.0, landform.elevationFactor * 0.4)
      const r = baseRadius + elevationOffset
      return {
        landform,
        localPos: new THREE.Vector3(nx * r, ny * r, nz * r),
        centerUnit: new THREE.Vector3(nx, ny, nz).normalize(),
        elevationOffset,
      }
    })
  }, [landforms, baseRadius, maxAltitude])

  // Pre-seed pseudo-random agents for smooth deterministic flight paths
  const boidAgents = useMemo(() => {
    const agentsBySpecies: Record<string, BoidAgent[]> = {}

    species.forEach((spec) => {
      const list: BoidAgent[] = []
      const maxCount = spec.population || 40

      for (let i = 0; i < maxCount; i++) {
        const landformIdx = i % Math.max(1, landforms.length)
        const lf = landforms[landformIdx]
        const plateRadius = lf?.plateRadius || 0.3

        let baseAlt = baseRadius + 10.0
        if (spec.type === 'avian_glider') {
          baseAlt =
            baseRadius +
            maxAltitude * 0.5 +
            spec.boidPhysics.terrainAvoidanceAltitude * 0.4
        } else if (spec.type === 'pelagic_swimmer') {
          baseAlt =
            baseRadius * (1.002 + seaLevel * 0.015) +
            spec.boidPhysics.terrainAvoidanceAltitude * 0.25
        } else {
          baseAlt = baseRadius + 7.0 + (i % 5) * 2.0
        }

        list.push({
          speciesType: spec.type,
          landformIndex: landformIdx,
          orbitRadius: 8.0 + (i % 7) * (plateRadius * 18.0 + 1.2),
          orbitSpeed:
            (0.3 + (i % 5) * 0.15) *
            (spec.boidPhysics.maxSpeed / 5.0) *
            (i % 2 === 0 ? 1 : -1),
          baseAltitude: baseAlt + (i % 4) * 2.0,
          phaseOffset: (i * 1.618) % (Math.PI * 2),
          verticalFreq: 0.8 + (i % 3) * 0.4,
          wobbleFreq: 1.2 + (i % 4) * 0.5,
        })
      }
      agentsBySpecies[spec.type] = list
    })

    return agentsBySpecies
  }, [species, landforms, baseRadius, maxAltitude, seaLevel])

  // Simulation frame: Smart LoD gating & Sector Proximity Culling
  useFrame((state) => {
    if (!groupRef.current) return

    // 1. Distance-gated visibility check:
    // When camera is pulled back (orbit distance > 185), lifeforms are culled
    state.camera.getWorldPosition(_scratchCamPos)
    const cameraDistanceToOrigin = _scratchCamPos.length()

    if (!isLodActive(cameraDistanceToOrigin, LOD_DISTANCE_THRESHOLD)) {
      if (groupRef.current.visible) {
        groupRef.current.visible = false
      }
      return
    }

    if (!groupRef.current.visible) {
      groupRef.current.visible = true
    }

    // 2. Identify landforms in proximity / field of view
    const planetMatrix = groupRef.current.matrixWorld
    const activeLandformIndices = new Set<number>()

    for (let i = 0; i < landformLocalPositions.length; i++) {
      const item = landformLocalPositions[i]
      if (!item) continue
      _scratchLandformWorld.copy(item.localPos).applyMatrix4(planetMatrix)

      if (
        isSectorInProximity(
          _scratchCamPos,
          _scratchLandformWorld,
          SECTOR_PROXIMITY_THRESHOLD
        )
      ) {
        activeLandformIndices.add(i)
      }
    }

    const t = state.clock.getElapsedTime()

    // 3. Simulate and render only lifeforms inhabiting active landform sectors
    for (const spec of species) {
      const mesh = meshesRef.current[spec.type]
      if (!mesh) continue

      const agents = boidAgents[spec.type] || []
      let activeCount = 0

      for (let i = 0; i < agents.length; i++) {
        const agent = agents[i]
        if (!agent) continue

        // Proximity Culling: Only simulate lifeforms belonging to active sectors
        if (!activeLandformIndices.has(agent.landformIndex)) {
          continue
        }

        const lfItem = landformLocalPositions[agent.landformIndex]
        if (!lfItem) continue

        // Compute local tangent plane coordinates (u, v) perpendicular to landform normal
        const normal = lfItem.centerUnit
        if (Math.abs(normal.y) < 0.99) {
          _tangentU.set(-normal.z, 0, normal.x).normalize()
        } else {
          _tangentU.set(1, 0, 0).normalize()
        }
        _tangentV.crossVectors(normal, _tangentU).normalize()

        // Keplerian orbit & flocking position around landform center
        const angle = t * agent.orbitSpeed + agent.phaseOffset
        const rOrbit =
          agent.orbitRadius +
          Math.sin(t * agent.wobbleFreq + agent.phaseOffset) * 2.5
        const alt =
          agent.baseAltitude +
          Math.sin(t * agent.verticalFreq + agent.phaseOffset) * 1.8

        _boidPos
          .copy(lfItem.centerUnit)
          .multiplyScalar(alt)
          .addScaledVector(_tangentU, Math.cos(angle) * rOrbit)
          .addScaledVector(_tangentV, Math.sin(angle) * rOrbit)

        // Compute velocity direction tangent to orbit
        _forward
          .copy(_tangentU)
          .multiplyScalar(-Math.sin(angle) * agent.orbitSpeed)
          .addScaledVector(_tangentV, Math.cos(angle) * agent.orbitSpeed)
          .normalize()

        _dummy.position.copy(_boidPos)

        if (_forward.lengthSq() > 0.001) {
          const targetLook = _boidPos.clone().add(_forward)
          _dummy.lookAt(targetLook)
        }

        // Slight bioluminescent pulse scale modulation
        const pulse =
          1.0 +
          Math.sin(t * spec.pulseFrequency * 3.0 + agent.phaseOffset) * 0.12
        _dummy.scale.setScalar(pulse)

        _dummy.updateMatrix()
        mesh.setMatrixAt(activeCount, _dummy.matrix)
        activeCount++
      }

      mesh.count = activeCount
      mesh.instanceMatrix.needsUpdate = true
    }
  })

  return (
    <group ref={groupRef} name="lifeforms-ecosystem">
      {species.map((spec) => (
        <SpeciesMeshUnit
          key={spec.type}
          species={spec}
          meshRef={(el) => {
            if (el) {
              meshesRef.current[spec.type] = el
            } else {
              delete meshesRef.current[spec.type]
            }
          }}
        />
      ))}
    </group>
  )
}
