import { useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

interface CosmicBackgroundProps {
  starCount?: number
  dustCount?: number
}

// Deterministic pseudorandom generator for starfield positioning
function createSeededRandom(seed = 42) {
  let s = seed
  return () => {
    s = (s * 9301 + 49297) % 233280
    return s / 233280
  }
}

function generateStars(count: number): [Float32Array, Float32Array, Float32Array] {
  const rng = createSeededRandom(1337)
  const positions = new Float32Array(count * 3)
  const colors = new Float32Array(count * 3)
  const sizes = new Float32Array(count)

  const colorChoices = [
    new THREE.Color('#ffffff'),
    new THREE.Color('#d4e6f1'),
    new THREE.Color('#f9e79f'),
    new THREE.Color('#a29bfe'),
    new THREE.Color('#81ecec'),
  ]

  for (let i = 0; i < count; i++) {
    const u = rng()
    const v = rng()
    const theta = u * 2.0 * Math.PI
    const phi = Math.acos(2.0 * v - 1.0)
    const r = 800.0 + rng() * 800.0

    positions[i * 3] = r * Math.sin(phi) * Math.cos(theta)
    positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta)
    positions[i * 3 + 2] = r * Math.cos(phi)

    const color = colorChoices[Math.floor(rng() * colorChoices.length)]
    colors[i * 3] = color.r
    colors[i * 3 + 1] = color.g
    colors[i * 3 + 2] = color.b

    sizes[i] = 1.0 + rng() * 2.5
  }

  return [positions, colors, sizes]
}

function generateDust(count: number): Float32Array {
  const rng = createSeededRandom(9001)
  const positions = new Float32Array(count * 3)

  for (let i = 0; i < count; i++) {
    const u = rng()
    const v = rng()
    const theta = u * 2.0 * Math.PI
    const phi = Math.acos(2.0 * v - 1.0)
    const r = 250.0 + rng() * 350.0

    positions[i * 3] = r * Math.sin(phi) * Math.cos(theta)
    positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta)
    positions[i * 3 + 2] = r * Math.cos(phi)
  }

  return positions
}

export function CosmicBackground({
  starCount = 3500,
  dustCount = 800,
}: CosmicBackgroundProps) {
  const starsRef = useRef<THREE.Points>(null)
  const dustRef = useRef<THREE.Points>(null)

  const [starPositions, starColors, starSizes] = useMemo(
    () => generateStars(starCount),
    [starCount]
  )

  const dustPositions = useMemo(
    () => generateDust(dustCount),
    [dustCount]
  )

  // Subtle cosmic drift animation loop
  useFrame((_, delta) => {
    if (starsRef.current) {
      starsRef.current.rotation.y += delta * 0.005
      starsRef.current.rotation.x += delta * 0.002
    }
    if (dustRef.current) {
      dustRef.current.rotation.y -= delta * 0.008
      dustRef.current.rotation.z += delta * 0.003
    }
  })

  return (
    <group>
      {/* Deep Space Black Void Ambient */}
      <color attach="background" args={['#030308']} />

      {/* Distant Twinkling Starfield */}
      <points ref={starsRef}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            args={[starPositions, 3]}
          />
          <bufferAttribute attach="attributes-color" args={[starColors, 3]} />
          <bufferAttribute attach="attributes-size" args={[starSizes, 1]} />
        </bufferGeometry>
        <pointsMaterial
          size={1.8}
          vertexColors
          transparent
          opacity={0.85}
          sizeAttenuation
          depthWrite={false}
        />
      </points>

      {/* Drifting Cosmic Space Dust */}
      <points ref={dustRef}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            args={[dustPositions, 3]}
          />
        </bufferGeometry>
        <pointsMaterial
          size={1.2}
          color="#6c5ce7"
          transparent
          opacity={0.35}
          sizeAttenuation
          depthWrite={false}
        />
      </points>
    </group>
  )
}
