import './SatelliteInfo.css';

export default function SatelliteInfo({ satellite, onClose }) {
  if (!satellite) return null;

  return (
    <div className="satellite-info">
      <button className="close-btn" onClick={onClose}>
        ×
      </button>

      <h2 className="satellite-name">{satellite.name}</h2>

      <div className="satellite-details">
        <div className="detail-row">
          <span className="label">NORAD ID:</span>
          <span className="value">{satellite.norad_id}</span>
        </div>

        <div className="detail-row">
          <span className="label">Latitude:</span>
          <span className="value">{satellite.latitude?.toFixed(4)}°</span>
        </div>

        <div className="detail-row">
          <span className="label">Longitude:</span>
          <span className="value">{satellite.longitude?.toFixed(4)}°</span>
        </div>

        <div className="detail-row">
          <span className="label">Altitude:</span>
          <span className="value">{satellite.altitude?.toFixed(2)} km</span>
        </div>

        {satellite.velocity && (
          <div className="detail-row">
            <span className="label">Velocity:</span>
            <span className="value">{satellite.velocity.toFixed(2)} km/h</span>
          </div>
        )}

        {satellite.type && (
          <div className="detail-row">
            <span className="label">Type:</span>
            <span className="value">{satellite.type}</span>
          </div>
        )}
      </div>
    </div>
  );
}
