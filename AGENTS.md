# DevPlanet - Agent Context File (AGENTS.md)

Welcome, Agent! This file serves as the core context for the DevPlanet project. Read this to get up to speed instantly without needing the entire conversation history.

## Project Overview
**DevPlanet** transforms a user's GitHub profile into a highly interactive, procedurally generated 3D planet.
*   **The User** = The Planet.
*   **Repositories** = Landforms (mountains, continents).
*   **Engagement (Stars/Forks)** = Lifeforms/Inhabitants (simulated via Boids/ECS).
*   **External Contributions** = Moons or asteroid rings orbiting the planet.
*   **Biomes & Weather** = Purely mathematical procedural generation: Shannon language entropy, continuous Whittaker/Oklab climate matrix, Fourier circadian commit rhythms, and spherical harmonic FBM heightfields. *No static themes or hardcoded biomes.*

## Architecture & Tech Stack
We use a containerized, polyglot microservice approach designed to be highly scalable and cost-effective on a VPS (avoiding expensive PaaS vendor lock-in).
*   **`api/` (Go):** API Gateway and Data Ingestion. Handles GitHub GraphQL fetching, Redis caching, and async task queuing.
*   **`forge/` (Python):** The algorithmic engine. Uses NumPy/SciPy for vectorized noise math, continuous Oklab color blending, and Boids ecosystem parameterization. Generates the JSON "Planet Genome."
*   **`canvas/` (TypeScript / React / Three.js / R3F):** The frontend SPA. Uses WebGL shaders for instant planet rendering (with Level of Detail zooming) and ECS for lifeform simulation. No server-side rendering.
*   **Infrastructure:** Docker Compose, PostgreSQL (JSONB), Redis, Nginx, Cloudflare CDN.

## Repository Structure
This is a monorepo containing all services:
- `/api` - Go backend codebase (Data ingestion, Redis caching & task queueing)
  - `/api/test/` - Consolidated Go test directory (e.g. `/api/test/unit/`)
- `/forge` - Python algorithmic engine codebase (Procedural generation)
  - `/forge/test/` - Consolidated Python test directory (e.g. `/forge/test/unit/`)
- `/canvas` - TypeScript frontend codebase (3D WebGL renderer)
  - `/canvas/test/` - Consolidated frontend test directory
- `/docs` - Architecture specifications and design docs

## Branching & CodeRabbit Quality Gate
To maintain high code quality, test integrity, and strict isolation across layers, **no direct pushes to `main` are permitted for feature development**.

### 1. Layer-Specific Branching Convention
- **Format:** `<type>/<layer>-<feature-description>`
  - Types: `feat`, `fix`, `refactor`, `test`, `perf`
  - Layers: `api`, `forge`, `canvas`, `infra`
  - Examples:
    - `feat/forge-scaffold-and-contracts`
    - `feat/forge-seeder-and-math-engine`
    - `feat/forge-spherical-topology`
    - `feat/canvas-threejs-setup`
- **Layer Isolation:** Feature branches must strictly modify their respective layer (`api/`, `forge/`, or `canvas/`). Cross-layer changes should only occur for shared contracts or Docker Compose updates.

### 2. CodeRabbit AI PR Reviews
- Every Pull Request targeting `main` is automatically reviewed by **CodeRabbit** according to `.coderabbit.yaml`.
- **Review Directives by Layer:**
  - **`api/` (Go):** Concurrency safety, context cancellation, goroutine leak checks, strict test placement in `api/test/`, Redis connection pooling, and GraphQL rate limit safety.
  - **`forge/` (Python):** NumPy vectorization over raw loops, deterministic PRNG seeding, continuous climate/Oklab math, and strict test containment in `forge/test/`.
  - **`canvas/` (TypeScript / WebGL):** GPU resource cleanup/disposal, 60 FPS main thread guarantee, draw call minimization (InstancedMesh/LOD), and pure SPA architecture (no SSR).
- **Merge Criteria:** All critical CodeRabbit feedback and developer reviews must be resolved before merging into `main`.

## Current Status & Milestones
*   **Completed:**
    *   Project conception & architectural design.
    *   Monorepo scaffolding & root `.gitignore`.
    *   Go API module initialized (`api/go.mod`).
    *   GitHub GraphQL query & client implementation (`api/internal/github/`).
    *   Redis caching & async task queueing with workers (`api/internal/store/`, `cache/`, `queue/`, `worker/`).
    *   Consolidated test suites in `api/test/unit/`.
    *   CodeRabbit configuration (`.coderabbit.yaml`) & Branching strategy established.
    *   *The Forge* Phase 1: Foundation & Pydantic v2 data contracts.
    *   *The Forge* Phase 2: Deterministic Seeder (`seeder.py`) & Vectorized Math Profiling (`math_profile.py`).
    *   *The Forge* Phase 3: Spherical Topology Engine on $S^2$ (`feat/forge-spherical-topology`):
        - Fibonacci sphere lattice distribution with deterministic seeded organic jitter.
        - Primary repository sifting (top 12 maximum) and plate mass weighting.
        - Geological tectonic archetype classification (`orogenic_belt`, `shield_craton`, `volcanic_archipelago`, `rift_valley`, `oceanic_trench`).
        - Continuous coupling of Shannon entropy to fractal octaves, sea level, and domain warping.
        - 19 passing unit tests in `forge/test/unit/`.
*   **Next Immediate Tasks:**
    *   *The Forge* Phase 4: Continuous Oklab Color Space & Climate Matrix Synthesizer (`forge/src/engine/palette.py` & `climate.py`).
    *   *The Forge* Phase 5: Celestial Mechanics (Moons, Rings) & Inhabitant Boids Ecosystem (`celestial.py`, `ecosystem.py`).

## Agent Instructions
1. Always work within the active feature branch designated for the specific layer.
2. Maintain strict segregation between the `api`, `forge`, and `canvas` layers.
3. Write modular, performant code suitable for a lean VPS deployment.
4. Keep all tests organized inside dedicated test directories (`test/unit/`) rather than scattered in internal packages.
5. The user acts as the lead developer; provide code for review incrementally and ensure you are aligned on direction before making massive multi-file changes.
6. Keep this `AGENTS.md` file updated as major milestones are completed or architecture shifts.
