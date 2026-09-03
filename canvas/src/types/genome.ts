/**
 * TypeScript data contracts mirroring The Forge's Pydantic v2 PlanetGenome schema.
 */

export interface MetaGenome {
  username: string
  masterSeed: string
  generatedAt: string
  version: string
}

export interface MathematicalProfile {
  shannonEntropy: number
  diurnalPhase: number
  diurnalCoherence: number
  repoGiniIndex: number
  polyglotDiversity: number
}

export interface CelestialMoon {
  id: string
  name: string
  radius: number
  orbitRadius: number
  orbitSpeed: number
  inclination: number
  color: string
  craterDensity: number
}

export interface CelestialRings {
  enabled: boolean
  innerRadius: number
  outerRadius: number
  particleCount: number
  density: number
  tint: string
}

export interface CelestialGenome {
  radius: number
  rotationSpeed: number
  axialTilt: number
  moons: CelestialMoon[]
  rings: CelestialRings
}

export interface LandformNode {
  repoName: string
  plateCenter: [number, number, number] // [x, y, z] unit vector on S^2
  plateRadius: number
  elevationFactor: number
  roughness: number
}

export interface TopologyGenome {
  baseRadius: number
  seaLevel: number
  maxAltitude: number
  octaves: number
  persistence: number
  lacunarity: number
  domainWarpFrequency: number
  domainWarpAmplitude: number
  landforms: LandformNode[]
}

export interface ElevationRampNode {
  elevation: number
  oklab: [number, number, number]
  hex: string
}

export interface SurfaceMaterialGenome {
  temperatureBase: number
  equatorHeat: number
  polarCooling: number
  moistureBase: number
  oceanEvaporation: number
  roughnessCurve: number[]
  metallicFactor: number
  crystallineFacetting: number
  elevationColorRamp: ElevationRampNode[]
}

export interface BoidPhysics {
  maxSpeed: number
  maxForce: number
  separationDist: number
  neighborRadius: number
  cohesionWeight: number
  alignmentWeight: number
  separationWeight: number
  terrainAvoidanceAltitude: number
}

export interface InhabitantSpecies {
  type: string
  population: number
  meshArchetype: string
  scale: number
  boidPhysics: BoidPhysics
  bioluminescenceColor: string
  pulseFrequency: number
}

export interface EcosystemGenome {
  species: InhabitantSpecies[]
  auroraIntensity: number
  auroraFrequency: number
  auroraColor: string
}

export interface AtmosphereGenome {
  hasAtmosphere: boolean
  densityScaleHeight: number
  rayleighCoefficients: [number, number, number] // (R, G, B)
  mieCoefficient: number
  mieDirectionalG: number
  cloudCover: number
  cloudSpeed: number
}

export interface PlanetGenome {
  meta: MetaGenome
  mathProfile: MathematicalProfile
  celestial: CelestialGenome
  topology: TopologyGenome
  surfaceMaterial: SurfaceMaterialGenome
  ecosystem: EcosystemGenome
  atmosphere: AtmosphereGenome
}

export interface LandformRepoStat {
  name: string
  description?: string | null
  stars: number
  forks: number
  commitCount: number
  primaryLanguage?: {
    name: string
    color: string
  } | null
}
