import * as THREE from 'three'
import { describe, expect, it } from 'vitest'
import type { LandformNode } from '@/types/genome'
import {
  getActiveSectors,
  getLandformWorldPosition,
  isLodActive,
  isSectorInProximity,
  LOD_DISTANCE_THRESHOLD,
  SECTOR_PROXIMITY_THRESHOLD,
} from '@/utils/boidsLod'

describe('LoD & Sector Proximity Calculation (boidsLod)', () => {
  describe('isLodActive', () => {
    it('returns false when camera distance exceeds default threshold (185 units)', () => {
      expect(isLodActive(185.1)).toBe(false)
      expect(isLodActive(250.0)).toBe(false)
      expect(isLodActive(320.0)).toBe(false) // Initial macro orbit view
      expect(isLodActive(850.0)).toBe(false)
    })

    it('returns true when camera distance is at or within threshold (<= 185 units)', () => {
      expect(isLodActive(185.0)).toBe(true)
      expect(isLodActive(160.0)).toBe(true)
      expect(isLodActive(125.0)).toBe(true) // Minimum zoom orbit distance
      expect(isLodActive(50.0)).toBe(true)
    })

    it('supports custom distance threshold parameter', () => {
      expect(isLodActive(100, 90)).toBe(false)
      expect(isLodActive(80, 90)).toBe(true)
      expect(isLodActive(LOD_DISTANCE_THRESHOLD, LOD_DISTANCE_THRESHOLD)).toBe(true)
    })
  })

  describe('isSectorInProximity', () => {
    it('returns true when camera is within proximity threshold of the landform', () => {
      const cameraPos = new THREE.Vector3(0, 0, 150)
      const landformPos = new THREE.Vector3(0, 0, 100)

      expect(isSectorInProximity(cameraPos, landformPos, SECTOR_PROXIMITY_THRESHOLD)).toBe(true)
      expect(isSectorInProximity(cameraPos, landformPos, 40.0)).toBe(false) // distance is 50
      expect(isSectorInProximity(cameraPos, landformPos, 50.0)).toBe(true)
    })

    it('returns false when landform is on opposite side of planet or far beyond threshold', () => {
      const cameraPos = new THREE.Vector3(0, 0, 150)
      // Opposite side of the planet (distance = 250)
      const landformOpposite = new THREE.Vector3(0, 0, -100)

      expect(isSectorInProximity(cameraPos, landformOpposite, SECTOR_PROXIMITY_THRESHOLD)).toBe(false)
    })
  })

  describe('getLandformWorldPosition & getActiveSectors', () => {
    const dummyLandforms: LandformNode[] = [
      {
        repoName: 'near-sector',
        plateCenter: [0, 0, 1],
        plateRadius: 0.3,
        elevationFactor: 1.5,
        roughness: 0.5,
      },
      {
        repoName: 'far-sector',
        plateCenter: [0, 0, -1],
        plateRadius: 0.3,
        elevationFactor: 1.5,
        roughness: 0.5,
      },
    ]

    it('correctly maps local landform position through planet transform matrix', () => {
      const localPos = new THREE.Vector3(0, 100, 0)
      const matrix = new THREE.Matrix4().makeTranslation(10, 20, 30)

      const worldPos = getLandformWorldPosition(localPos, matrix)
      expect(worldPos.x).toBeCloseTo(10)
      expect(worldPos.y).toBeCloseTo(120)
      expect(worldPos.z).toBeCloseTo(30)
    })

    it('filters active sectors according to proximity to camera', () => {
      const identityMatrix = new THREE.Matrix4()
      const items = [
        {
          landform: dummyLandforms[0]!,
          localPos: new THREE.Vector3(0, 0, 100),
        },
        {
          landform: dummyLandforms[1]!,
          localPos: new THREE.Vector3(0, 0, -100),
        },
      ]

      const cameraNearFront = new THREE.Vector3(0, 0, 140)
      const active = getActiveSectors(items, cameraNearFront, identityMatrix, 160)

      expect(active).toHaveLength(1)
      expect(active[0]?.repoName).toBe('near-sector')
    })
  })
})
