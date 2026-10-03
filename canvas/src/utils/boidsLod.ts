import * as THREE from 'three'
import type { LandformNode } from '@/types/genome'

export const LOD_DISTANCE_THRESHOLD = 185.0
export const SECTOR_PROXIMITY_THRESHOLD = 160.0

/**
 * Determines whether Level of Detail (LoD) lifeform simulation is active
 * based on camera distance to planet center (origin [0, 0, 0]).
 */
export function isLodActive(
  cameraDistance: number,
  threshold: number = LOD_DISTANCE_THRESHOLD
): boolean {
  return cameraDistance <= threshold
}

/**
 * Computes world position of a landform given its local position and planet transform matrix.
 */
export function getLandformWorldPosition(
  localPos: THREE.Vector3,
  planetMatrixWorld: THREE.Matrix4,
  target: THREE.Vector3 = new THREE.Vector3()
): THREE.Vector3 {
  target.copy(localPos)
  target.applyMatrix4(planetMatrixWorld)
  return target
}

/**
 * Checks if a landform sector is in camera proximity / view field.
 */
export function isSectorInProximity(
  cameraWorldPos: THREE.Vector3,
  landformWorldPos: THREE.Vector3,
  threshold: number = SECTOR_PROXIMITY_THRESHOLD
): boolean {
  return cameraWorldPos.distanceTo(landformWorldPos) <= threshold
}

/**
 * Filter landforms that are currently active based on camera proximity.
 */
export function getActiveSectors(
  landforms: { landform: LandformNode; localPos: THREE.Vector3 }[],
  cameraWorldPos: THREE.Vector3,
  planetMatrixWorld: THREE.Matrix4,
  threshold: number = SECTOR_PROXIMITY_THRESHOLD
): LandformNode[] {
  const scratchWorld = new THREE.Vector3()
  const active: LandformNode[] = []

  for (const item of landforms) {
    getLandformWorldPosition(item.localPos, planetMatrixWorld, scratchWorld)
    if (isSectorInProximity(cameraWorldPos, scratchWorld, threshold)) {
      active.push(item.landform)
    }
  }

  return active
}
