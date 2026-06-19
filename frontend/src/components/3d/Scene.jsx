import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import { useState, useCallback } from 'react';
import Earth from './Earth';
import Satellite from './Satellite';
import OrbitPath from './OrbitPath';
// ИМПОРТИРУЕМ ФУНКЦИЮ (проверьте правильность пути к файлу)
import { llaToThree } from '../../utils/coordinates';

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
      <ambientLight intensity={0.3} />
      <directionalLight position={[5, 3, 5]} intensity={1} />
      <pointLight position={[-5, -3, -5]} intensity={0.5} />
      <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
      
      <Earth textures={textures} />

      {satellites.map((satellite) => (
        <group key={satellite.norad_id}>
          
          {satellite.orbit_points && (
            <OrbitPath orbitPoints={satellite.orbit_points} />
          )}

          {/* ИСПРАВЛЕНО: Используем LLA (Широту, Долготу, Высоту) вместо ECEF */}
          {satellite.latitude !== undefined && satellite.longitude !== undefined && (
            <Satellite
              // Вызываем ту же функцию, что и для точек орбиты
              position={llaToThree(
                satellite.latitude, 
                satellite.longitude, 
                satellite.altitude
              )}
              onClick={() => handleSatelliteClick(satellite)}
              color={selectedSatellite?.norad_id === satellite.norad_id ? '#ff0000' : '#ff6600'}
            />
          )}
        </group>
      ))}

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