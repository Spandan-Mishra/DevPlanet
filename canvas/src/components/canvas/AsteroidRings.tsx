import { useEffect, useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import type { CelestialRings } from '@/types/genome'

interface AsteroidRingsProps {
  rings: CelestialRings
}

// Deterministic PRNG for asteroid placement
function createSeededRandom(seed = 777) {
  let s = seed
  return () => {
    s = (s * 9301 + 49297) % 233280
    return s / 233280
  }
}

interface AsteroidOrbit {
  radius: number
  angle: number
  verticalJitter: number
  scale: number
  speed: number
  rotAngle: number
  rotSpeed: number
}

export function AsteroidRings({ rings }: AsteroidRingsProps) {
  const instancedMeshRef = useRef<THREE.InstancedMesh>(null)
  const orbitsRef = useRef<AsteroidOrbit[]>([])

  const particleCount = Math.min(rings.particleCount, 2500)

  // Initialize orbital parameters in mutable ref to avoid mutating useMemo return
  useEffect(() => {
    const rng = createSeededRandom(404)
    const data: AsteroidOrbit[] = []

    for (let i = 0; i < particleCount; i++) {
      const radius =
        rings.innerRadius +
        rng() * (rings.outerRadius - rings.innerRadius)
      const angle = rng() * Math.PI * 2.0
      const verticalJitter = (rng() - 0.5) * 4.5
      const scale = 0.4 + rng() * 1.2
      // Keplerian angular velocity inversely proportional to radius^(1.5)
      const speed = (0.25 / Math.pow(radius / 100.0, 1.5)) * (0.9 + rng() * 0.2)
      const rotSpeed = (rng() - 0.5) * 1.5

      data.push({
        radius,
        angle,
        verticalJitter,
        scale,
        speed,
        rotAngle: rng() * Math.PI,
        rotSpeed,
      })
    }

    orbitsRef.current = data

    if (instancedMeshRef.current) {
      const dummy = new THREE.Object3D()
      for (let i = 0; i < particleCount; i++) {
        const orb = data[i]
        const x = Math.cos(orb.angle) * orb.radius
        const z = Math.sin(orb.angle) * orb.radius
        dummy.position.set(x, orb.verticalJitter, z)
        dummy.rotation.set(orb.rotAngle, orb.rotAngle * 0.5, 0)
        dummy.scale.set(orb.scale, orb.scale * 0.8, orb.scale)
        dummy.updateMatrix()
        instancedMeshRef.current.setMatrixAt(i, dummy.matrix)
      }
      instancedMeshRef.current.instanceMatrix.needsUpdate = true
    }
  }, [particleCount, rings.innerRadius, rings.outerRadius])

  const dummy = useMemo(() => new THREE.Object3D(), [])

  // Keplerian orbital animation loop
  useFrame((_, delta) => {
    if (!instancedMeshRef.current || orbitsRef.current.length === 0) return

    const orbits = orbitsRef.current
    for (let i = 0; i < particleCount; i++) {
      const orb = orbits[i]
      if (!orb) continue

      orb.angle += orb.speed * delta * 0.4
      orb.rotAngle += orb.rotSpeed * delta

      const x = Math.cos(orb.angle) * orb.radius
      const z = Math.sin(orb.angle) * orb.radius

      dummy.position.set(x, orb.verticalJitter, z)
      dummy.rotation.set(orb.rotAngle, orb.rotAngle * 0.5, orb.rotAngle * 0.3)
      dummy.scale.set(orb.scale, orb.scale * 0.8, orb.scale)
      dummy.updateMatrix()
      instancedMeshRef.current.setMatrixAt(i, dummy.matrix)
    }
    instancedMeshRef.current.instanceMatrix.needsUpdate = true
  })

  return (
    <group rotation={[Math.PI / 2 + 0.1, 0, 0]}>
      {/* 1. Instanced 3D Asteroid Debris Rocks (frustumCulled={false} keeps dynamic orbit visible) */}
      <instancedMesh
        ref={instancedMeshRef}
        args={[undefined, undefined, particleCount]}
        frustumCulled={false}
        castShadow
        receiveShadow
      >
        <dodecahedronGeometry args={[0.9, 0]} />
        <meshStandardMaterial
          color={rings.tint}
          roughness={0.9}
          metalness={0.15}
        />
      </instancedMesh>

      {/* 2. Soft Micro-Dust Translucent Disc Underlay */}
      <mesh>
        <ringGeometry
          args={[rings.innerRadius, rings.outerRadius, 96]}
        />
        <meshStandardMaterial
          color={rings.tint}
          side={THREE.DoubleSide}
          transparent
          opacity={rings.density * 0.45}
          roughness={0.8}
          depthWrite={false}
        />
      </mesh>
    </group>
  )
}
