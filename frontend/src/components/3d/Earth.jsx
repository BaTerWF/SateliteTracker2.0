import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Sphere } from '@react-three/drei';
import * as THREE from 'three';

export default function Earth({ textures = {} }) {
  const earthRef = useRef();

  // Earth radius in km (scaled for visualization)
  const EARTH_RADIUS_KM = 6371;

  // Convert km to Three.js units (scale factor)
  const SCALE = 0.0003;
  const radius = EARTH_RADIUS_KM * SCALE;

  useFrame((state, delta) => {
    if (earthRef.current) {
      // Rotate earth slowly
      earthRef.current.rotation.y += delta * 0;
    }
  });

  return (
    <Sphere ref={earthRef} args={[radius, 64, 64]}>
      <meshPhongMaterial
        map={textures.color}
        bumpMap={textures.bump}
        bumpScale={0.05}
        specularMap={textures.specular}
        specular={new THREE.Color('grey')}
        shininess={10}
      />
    </Sphere>
  );
}
