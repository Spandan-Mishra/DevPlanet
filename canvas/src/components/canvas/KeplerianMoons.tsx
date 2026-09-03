import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import type { CelestialMoon } from '@/types/genome'

interface KeplerianMoonsProps {
  moons: CelestialMoon[]
}

interface SingleMoonProps {
  moon: CelestialMoon
}

function SingleMoon({ moon }: SingleMoonProps) {
  const moonGroupRef = useRef<THREE.Group>(null)

  // Rotate moon along its orbit based on its individual orbit speed
  useFrame((_, delta) => {
    if (moonGroupRef.current) {
      moonGroupRef.current.rotation.y += delta * moon.orbitSpeed * 0.35
    }
  })

  return (
    <group rotation={[moon.inclination, 0, 0]}>
      {/* Subtle Static Orbit Path Indicator Ring */}
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <ringGeometry
          args={[moon.orbitRadius - 0.25, moon.orbitRadius + 0.25, 64]}
        />
        <meshBasicMaterial
          color="#ffffff"
          transparent
          opacity={0.08}
          side={THREE.DoubleSide}
          depthWrite={false}
        />
      </mesh>

      {/* Rotating Moon Body Group */}
      <group ref={moonGroupRef}>
        <mesh
          position={[moon.orbitRadius, 0, 0]}
          castShadow
          receiveShadow
        >
          <sphereGeometry args={[moon.radius, 32, 32]} />
          <meshStandardMaterial
            color={moon.color}
            roughness={0.75 + moon.craterDensity * 0.2}
            metalness={0.08}
          />
        </mesh>
      </group>
    </group>
  )
}

export function KeplerianMoons({ moons }: KeplerianMoonsProps) {
  return (
    <group>
      {moons.map((moon) => (
        <SingleMoon key={moon.id} moon={moon} />
      ))}
    </group>
  )
}
