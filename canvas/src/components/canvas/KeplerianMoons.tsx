import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import type { CelestialMoon } from '@/types/genome'

interface KeplerianMoonsProps {
  moons: CelestialMoon[]
}

export function KeplerianMoons({ moons }: KeplerianMoonsProps) {
  const groupRef = useRef<THREE.Group>(null)

  // Rotate entire moon system around planet
  useFrame((_, delta) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += delta * 0.12
    }
  })

  return (
    <group ref={groupRef}>
      {moons.map((moon) => {
        return (
          <group
            key={moon.id}
            rotation={[moon.inclination, 0, 0]}
          >
            {/* Moon Celestial Body */}
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

            {/* Subtle Orbit Path Indicator Ring */}
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
          </group>
        )
      })}
    </group>
  )
}
