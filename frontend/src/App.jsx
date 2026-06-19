import { useState, useEffect, useRef } from 'react';
import Scene from './components/3d/Scene';
import Sidebar from './components/ui/Sidebar';
import SatelliteInfo from './components/ui/SatelliteInfo';
import Loader from './components/ui/Loader';
import { useSatellites } from './hooks/useSatellites';
import { usePolling } from './hooks/usePolling';
import './App.css';

function App() {
  const { satellites, loading, error, updateSatellitePosition } = useSatellites();
  const [selectedSatellite, setSelectedSatellite] = useState(null);
  const [textures, setTextures] = useState({});
  const texturesLoaded = useRef(false);

  // Load Earth textures
  useEffect(() => {
    const loadTextures = async () => {
      try {
        const textureLoader = new THREE.TextureLoader();

        const [colorMap, bumpMap, specularMap] = await Promise.all([
          textureLoader.loadAsync('/textures/earth_color.jpg'),
          textureLoader.loadAsync('/textures/earth_bump.jpg'),
          textureLoader.loadAsync('/textures/earth_specular.jpg'),
        ]);

        setTextures({
          color: colorMap,
          bump: bumpMap,
          specular: specularMap,
        });

        texturesLoaded.current = true;
      } catch (err) {
        console.warn('Failed to load Earth textures, using default materials:', err);
        texturesLoaded.current = true; // Continue without textures
      }
    };

    loadTextures();
  }, []);

  // Poll for satellite position updates every 5 seconds
  usePolling(
    () => {
      satellites.forEach((satellite) => {
        updateSatellitePosition(satellite.id).catch((err) => {
          console.warn(`Failed to update satellite ${satellite.id}:`, err);
        });
      });
    },
    5000,
    !loading && satellites.length > 0
  );

  const handleSatelliteClick = (satellite) => {
    setSelectedSatellite(satellite);
  };

  const handleCloseInfo = () => {
    setSelectedSatellite(null);
  };

  if (loading && !texturesLoaded.current) {
    return <Loader message="Loading Earth textures..." />;
  }

  if (error) {
    return (
      <div className="error-container">
        <h2>Error loading satellites</h2>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  return (
    <div className="app">
      {/* 3D Scene */}
      <Scene
        satellites={satellites}
        textures={textures}
        onSatelliteClick={handleSatelliteClick}
      />

      {/* UI Overlay */}
      <Sidebar
        satellites={satellites}
        onSatelliteSelect={handleSatelliteClick}
      />

      {/* Satellite Info Panel */}
      {selectedSatellite && (
        <SatelliteInfo
          satellite={selectedSatellite}
          onClose={handleCloseInfo}
        />
      )}

      {/* Loading indicator for initial data load */}
      {loading && (
        <div className="loading-indicator">Loading satellite data...</div>
      )}
    </div>
  );
}

export default App;
