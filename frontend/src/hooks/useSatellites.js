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
            const position = await satellitesAPI.getPosition(satellite.id);
            return {
              ...satellite,
              position: position.position,
              latitude: position.latitude,
              longitude: position.longitude,
              altitude: position.altitude,
              velocity: position.velocity,
            };
          } catch (err) {
            console.warn(`Failed to load position for satellite ${satellite.id}:`, err);
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

  const updateSatellitePosition = useCallback(async (satelliteId) => {
    try {
      const position = await satellitesAPI.getPosition(satelliteId);

      setSatellites(prev =>
        prev.map(sat =>
          sat.id === satelliteId
            ? {
                ...sat,
                position: position.position,
                latitude: position.latitude,
                longitude: position.longitude,
                altitude: position.altitude,
                velocity: position.velocity,
              }
            : sat
        )
      );

      return position;
    } catch (err) {
      console.error(`Failed to update position for satellite ${satelliteId}:`, err);
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
