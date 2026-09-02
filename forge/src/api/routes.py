from fastapi import APIRouter, status

from src.engine.orchestrator import PlanetGenomeOrchestrator
from src.models.genome import PlanetGenome
from src.models.request import UserPlanetProfileRequest

router = APIRouter(prefix="/api/v1/genome", tags=["Genome Generation"])


@router.post(
    "/generate",
    response_model=PlanetGenome,
    status_code=status.HTTP_200_OK,
    summary="Synthesize 3D Planet Genome",
    description="Procedurally transforms a GitHub developer ingestion payload into a complete deterministic PlanetGenome.",
)
async def generate_genome(request: UserPlanetProfileRequest) -> PlanetGenome:
    """Procedurally synthesizes the complete 3D Planet Genome."""
    return PlanetGenomeOrchestrator.synthesize_planet_genome(request)
