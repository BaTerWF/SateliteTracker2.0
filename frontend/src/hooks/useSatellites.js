import { useState, useEffect, useCallback } from 'react';
import { satellitesAPI } from '../api/satellites';

export function useSatellites() {
  const [satellites, setSatellites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 1. ПЕРВОНАЧАЛЬНАЯ ЗАГРУЗКА
  const loadSatellites = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await satellitesAPI.getAll();

      const satellitesWithPositions = await Promise.all(
        data.map(async (satellite) => {
          try {
            // Загружаем и позицию, и орбиту сразу при старте
            const [positionData, orbitData] = await Promise.all([
              satellitesAPI.getPosition(satellite.norad_id),
              satellitesAPI.getOrbit(satellite.norad_id)
            ]);
            
            return {
              ...satellite,
              position: positionData.position,
              latitude: positionData.latitude,
              longitude: positionData.longitude,
              altitude: positionData.altitude_km,
              velocity: positionData.speed_kmh,
              orbit_points: orbitData.points || [] // Добавляем точки орбиты!
            };
          } catch (err) {
            console.warn(`Failed to load data for satellite ${satellite.norad_id}:`, err);
            return satellite; 
          }
        })
      );

      setSatellites(satellitesWithPositions);
    } catch (err) {
      console.error('Failed to load satellites:', err);
      setError(err.message || 'Failed to load satellites');
    } finally {
      setLoading(false);
    }
  }, []);

  // 2. ФОНОВОЕ ОБНОВЛЕНИЕ (ПОЛЛИНГ)
  const updateSatellitePosition = useCallback(async (noradId) => {
    try {
      // ИСПОЛЬЗУЕМ noradId из аргумента функции
      const [positionData, orbitData] = await Promise.all([
        satellitesAPI.getPosition(noradId),
        satellitesAPI.getOrbit(noradId)
      ]);

      setSatellites(prev =>
        prev.map(sat =>
          sat.norad_id === noradId
            ? {
                ...sat,
                position: positionData.position,       // ИСПОЛЬЗУЕМ positionData
                latitude: positionData.latitude,
                longitude: positionData.longitude,
                altitude: positionData.altitude_km,
                velocity: positionData.speed_kmh,
                orbit_points: orbitData.points || sat.orbit_points 
              }
            : sat
        )
      );

      return positionData; // Возвращаем правильную переменную
    } catch (err) {
      console.error(`Failed to update position for satellite ${noradId}:`, err);
      throw err;
    }
  }, []);

  useEffect(() => {
    loadSatellites();
  }, [loadSatellites]);

  return {
    satellites,
    loading,
    error,
    loadSatellites,
    updateSatellitePosition,
  };
}