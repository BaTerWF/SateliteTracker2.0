import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import { useState, useCallback } from 'react';
import Earth from './Earth';
import Satellite from './Satellite';
import OrbitPath from './OrbitPath';

export default function Scene({ satellites, textures, onSatelliteClick }) {
  const [selectedSatellite, setSelectedSatellite] = useState(null);

  const handleSatelliteClick = useCallback((satellite) => {
    setSelectedSatellite(satellite);
    if (onSatelliteClick) {
      onSatelliteClick(satellite);
    }
  }, [onSatelliteClick]);

  return (
    <Canvas
      camera={{ position: [3, 2, 3], fov: 45 }}
      style={{ width: '100vw', height: '100vh' }}
    >
      {/* Lighting */}
      <ambientLight intensity={0.3} />
      <directionalLight position={[5, 3, 5]} intensity={1} />
      <pointLight position={[-5, -3, -5]} intensity={0.5} />

      {/* Background stars */}
      <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />

      {/* Earth */}
      <Earth textures={textures} />

      {/* Satellites and orbits */}
      {satellites.map((satellite) => (
        <group key={satellite.id}>
          {/* Orbit path */}
          {satellite.orbit_points && (
            <OrbitPath orbitPoints={satellite.orbit_points} />
          )}

          {/* Satellite marker */}
          {satellite.position && (
            <Satellite
              position={[
                satellite.position.x * 0.001,
                satellite.position.z * 0.001,
                -satellite.position.y * 0.001
              ]}
              onClick={() => handleSatelliteClick(satellite)}
              color={selectedSatellite?.id === satellite.id ? '#ff0000' : '#ff6600'}
            />
          )}
        </group>
      ))}

      {/* Camera controls */}
      <OrbitControls
        enableZoom={true}
        enablePan={true}
        enableRotate={true}
        minDistance={2}
        maxDistance={10}
      />
    </Canvas>
  );
}
