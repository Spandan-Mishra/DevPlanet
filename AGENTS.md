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
  - `/canvas/test/` - Consolidated frontend test directory (e.g. `/canvas/test/unit/`)
- `/docs` - Architecture specifications and design docs

## Agent Operating Model (Planner vs. Implementation)
Development follows a strict dual-agent paradigm:
1. **Planner Agent:**
   - Lives in the planning thread.
   - Plans architecture, reviews requirements, sequences work, tracks milestones, and formulates precise, self-contained implementation prompts.
   - **Does NOT emit implementation code.**
2. **Implementation Agent:**
   - Lives in a separate execution thread.
   - Receives tasks via prompts crafted by the Planner Agent.
   - Executes file edits, runs tests, performs verification, and commits changes incrementally.

## Implementation Agent Guidelines & Strict Directives
When implementing features or bug fixes, the Implementation Agent MUST follow these rules:
1. **Granular Commits (Strict Rule):**
   - **NEVER** push massive multi-hundred or 1,000+ line commits all at once.
   - Break work down into small, logical steps. For each step: make changes, test, and commit with an informative conventional commit message (`feat(canvas): ...`, `fix(canvas): ...`).
2. **Branching Convention:**
   - Branch format: `<type>/<layer>-<feature-description>` (e.g. `feat/canvas-smart-boids-and-repo-modal`).
   - Create branches strictly off the latest `main`.
3. **Layer Isolation:**
   - Keep changes restricted to the specified service layer (`canvas/`, `forge/`, or `api/`).
4. **Performance & Memory Management in WebGL (`canvas/`):**
   - **Smart Level of Detail (LoD):** Do not render distant micro-entities. Only render lifeforms/boids when the camera is sufficiently close to a landform and within the viewing frustum.
   - **Draw Call Minimization:** Use Three.js `InstancedMesh` for rendering recurring entities (boids, debris, flora).
   - **Resource Disposal:** Always clean up custom materials, geometries, and textures via `useEffect` dispose handlers to prevent GPU memory leaks.
5. **Quality Gates & Verification:**
   - Before completing any task, run the full verification pipeline:
     - Linter: `npx oxlint` (must pass with 0 errors).
     - Typecheck & Build: `npm run build` (`tsc -b && vite build`) (must pass with 0 errors).
     - Test Suite: `npx vitest run` (100% tests passing).

## Current Status & Milestones
*   **Completed:**
    *   Project conception & architectural design.
    *   Monorepo scaffolding & root `.gitignore`.
    *   Go API module initialized (`api/go.mod`).
    *   GitHub GraphQL query & client implementation (`api/internal/github/`).
    *   Redis caching & async task queueing with workers (`api/internal/store/`, `cache/`, `queue/`, `worker/`).
    *   Consolidated test suites in `api/test/unit/`.
    *   CodeRabbit configuration (`.coderabbit.yaml`) & Branching strategy established.
    *   *The Forge* (Python Procedural Engine) Phases 1 to 5 (PRs #1, #2, #3, #4, #5, #6 Merged).
    *   *The Canvas* Phase 1: SPA Scaffolding, R3F Viewport, Cosmic Background, and Legend Tooltip (PR #7 Merged).
    *   *The Canvas* Phase 2: Procedural GPU Terrain Shaders ($S^2$ FBM), Rayleigh/Mie Atmosphere, Instanced Asteroid Rings, Keplerian Moons (PR #8 Merged).
*   **Current Active Milestone:**
    *   *The Canvas* Phase 3:
        1. Smart camera distance / frustum-based Level-of-Detail (LoD) lifeform rendering (Boids) around zoomed landforms.
        2. Interactive Landform Click Modal: Rich GitHub repository summary card with glimpse metrics, topics, and quick actions.
