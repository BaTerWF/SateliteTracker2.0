import { useRef } from 'react';
import { Sphere } from '@react-three/drei';

export default function Satellite({ position, onClick, color = '#ff6600' }) {
  const meshRef = useRef();

  const handleClick = (event) => {
    // Останавливаем "пробитие" клика, чтобы не кликалась Земля под спутником
    event.stopPropagation(); 
    if (onClick) {
      onClick();
    }
  };

  return (
    <Sphere
      ref={meshRef}
      args={[0.015, 16, 16]}
      position={position}
      onClick={handleClick}
      // Увеличиваем зону клика (hitbox), если по маленькому спутнику трудно попасть мышкой
      scale={1.5} 
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