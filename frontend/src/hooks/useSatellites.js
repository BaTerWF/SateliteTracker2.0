import { useState, useEffect, useCallback } from 'react';
import { satellitesAPI } from '../api/satellites';

export function useSatellites() {
  const [satellites, setSatellites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadSatellites = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await satellitesAPI.getAll();

      // Transform API data to include positions if not already present
      const satellitesWithPositions = await Promise.all(
        data.map(async (satellite) => {
          try {
            // ИСПРАВЛЕНО: используем norad_id вместо id
            const position = await satellitesAPI.getPosition(satellite.norad_id);
            return {
              ...satellite,
              position: position.position,
              latitude: position.latitude,
              longitude: position.longitude,
              altitude: position.altitude_km,
              velocity: position.speed_kmh,
            };
          } catch (err) {
            // ИСПРАВЛЕНО: выводим norad_id в лог
            console.warn(`Failed to load position for satellite ${satellite.norad_id}:`, err);
            return satellite; // Возвращаем спутник без позиции, если произошла ошибка
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

  const updateSatellitePosition = useCallback(async (noradId) => {
    try {
      // ИСПРАВЛЕНО: передаем noradId
      const position = await satellitesAPI.getPosition(noradId);

      setSatellites(prev =>
        prev.map(sat =>
          // ИСПРАВЛЕНО: сравниваем sat.norad_id с переданным noradId
          sat.norad_id === noradId
            ? {
                ...sat,
                position: position.position,
                latitude: position.latitude,
                longitude: position.longitude,
                altitude: position.altitude_km,
                velocity: position.speed_kmh,
              }
            : sat
        )
      );

      return position;
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