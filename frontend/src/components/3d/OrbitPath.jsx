import { useMemo } from 'react';
import { Line } from '@react-three/drei';
import * as THREE from 'three';

export default function OrbitPath({ orbitPoints }) {
  // Convert orbit points to Three.js Vector3 array
  const points = useMemo(() => {
    if (!orbitPoints || orbitPoints.length === 0) return [];

    const SCALE = 0.001; // Same scale as Earth

    return orbitPoints.map(point => {
      // Assuming orbitPoints is array of {x, y, z} in ECEF coordinates (km)
      return new THREE.Vector3(
        point.x * SCALE,
        point.z * SCALE, // Swap Y and Z for Three.js coordinate system
        -point.y * SCALE
      );
    });
  }, [orbitPoints]);

  if (points.length === 0) return null;

  return (
    <Line
      points={points}
      color="#00ffff"
      lineWidth={1}
      opacity={0.5}
      transparent
    />
  );
}
