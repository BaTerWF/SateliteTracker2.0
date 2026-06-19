import { useMemo } from 'react';
import { Line } from '@react-three/drei';
import * as THREE from 'three';
import { llaToThree } from '../../utils/coordinates';

export default function OrbitPath({ orbitPoints }) {
  const points = useMemo(() => {
    if (!orbitPoints || orbitPoints.length === 0) return [];

    // Преобразуем каждую географическую точку [lat, lon, alt] в Vector3 для Three.js
    return orbitPoints.map(point => {
      const [x, y, z] = llaToThree(point.lat, point.lon, point.alt);
      return new THREE.Vector3(x, y, z);
    });
  }, [orbitPoints]);

  if (points.length === 0) return null;

  return (
    <Line
      points={points}
      color="#00ffff"
      lineWidth={1.5}
      opacity={0.6}
      transparent
    />
  );
}