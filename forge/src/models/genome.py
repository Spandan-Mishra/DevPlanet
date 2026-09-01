from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class ForgeBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class MetaGenome(ForgeBaseModel):
    username: str
    master_seed: str
    generated_at: str
    version: str = "1.0.0"


class MathematicalProfile(ForgeBaseModel):
    shannon_entropy: float
    diurnal_phase: float
    diurnal_coherence: float
    repo_gini_index: float
    polyglot_diversity: float


class CelestialMoon(ForgeBaseModel):
    id: str
    name: str
    radius: float
    orbit_radius: float
    orbit_speed: float
    inclination: float
    color: str
    crater_density: float


class CelestialRings(ForgeBaseModel):
    enabled: bool
    inner_radius: float
    outer_radius: float
    particle_count: int
    density: float
    tint: str


class CelestialGenome(ForgeBaseModel):
    radius: float
    rotation_speed: float
    axial_tilt: float
    moons: list[CelestialMoon] = []
    rings: CelestialRings


class LandformNode(ForgeBaseModel):
    repo_name: str
    plate_center: tuple[float, float, float]  # [x, y, z] on S^2
    plate_radius: float
    elevation_factor: float
    roughness: float
    tectonic_type: str
    resilience_index: float


class TopologyGenome(ForgeBaseModel):
    base_radius: float = Field(default=100.0, gt=0.0)
    sea_level: float = Field(default=0.45, ge=0.0, le=1.0)
    max_altitude: float = Field(default=25.0, gt=0.0)
    octaves: int = Field(default=6, ge=1, le=12)
    persistence: float = Field(default=0.5, gt=0.0, lt=1.0)
    lacunarity: float = Field(default=2.0, gt=1.0)
    domain_warp_frequency: float = Field(default=0.5, ge=0.0)
    domain_warp_amplitude: float = Field(default=10.0, ge=0.0)
    landforms: list[LandformNode] = []


class ElevationRampNode(ForgeBaseModel):
    elevation: float
    oklab: tuple[float, float, float]  # (L, a, b)
    hex: str


class SurfaceMaterialGenome(ForgeBaseModel):
    temperature_base: float
    equator_heat: float
    polar_cooling: float
    moisture_base: float
    ocean_evaporation: float
    roughness_curve: list[float]
    metallic_factor: float
    crystalline_facetting: float
    elevation_color_ramp: list[ElevationRampNode]


class BoidPhysics(ForgeBaseModel):
    max_speed: float
    max_force: float
    separation_dist: float
    neighbor_radius: float
    cohesion_weight: float
    alignment_weight: float
    separation_weight: float
    terrain_avoidance_altitude: float


class InhabitantSpecies(ForgeBaseModel):
    type: str
    population: int
    mesh_archetype: str
    scale: float
    boid_physics: BoidPhysics
    bioluminescence_color: str
    pulse_frequency: float


class EcosystemGenome(ForgeBaseModel):
    species: list[InhabitantSpecies] = []
    aurora_intensity: float
    aurora_frequency: float
    aurora_color: str


class AtmosphereGenome(ForgeBaseModel):
    has_atmosphere: bool
    density_scale_height: float
    rayleigh_coefficients: tuple[float, float, float]  # (R, G, B)
    mie_coefficient: float
    mie_directional_g: float
    cloud_cover: float
    cloud_speed: float


class PlanetGenome(ForgeBaseModel):
    meta: MetaGenome
    math_profile: MathematicalProfile
    celestial: CelestialGenome
    topology: TopologyGenome
    surface_material: SurfaceMaterialGenome
    ecosystem: EcosystemGenome
    atmosphere: AtmosphereGenome
