import { useRef } from 'react';
import { Sphere } from '@react-three/drei';
import * as THREE from 'three';

export default function Satellite({ position, onClick, color = '#ff6600' }) {
  const meshRef = useRef();

  const handleClick = (event) => {
    event.stopPropagation();
    if (onClick) {
      onClick();
    }
  };

  return (
    <Sphere
      ref={meshRef}
      args={[0.05, 16, 16]}
      position={position}
      onClick={handleClick}
    >
      <meshStandardMaterial
        color={color}
        emissive={color}
        emissiveIntensity={0.5}
        metalness={0.8}
        roughness={0.2}
      />
    </Sphere>
  );
}
