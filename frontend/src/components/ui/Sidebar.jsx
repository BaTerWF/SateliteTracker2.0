import { useState } from 'react';
import './Sidebar.css';

export default function Sidebar({ satellites, onSatelliteSelect }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');

  // Filter satellites based on search and type
  const filteredSatellites = satellites.filter(satellite => {
    const matchesSearch = satellite.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = filterType === 'all' || satellite.type === filterType;
    return matchesSearch && matchesType;
  });

  return (
    <div className="sidebar">
      <h2 className="sidebar-title">Satellites</h2>

      {/* Search */}
      <div className="search-container">
        <input
          type="text"
          placeholder="Search satellites..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />
      </div>

      {/* Filter */}
      <div className="filter-container">
        <label htmlFor="filter-select" className="filter-label">
          Filter by type:
        </label>
        <select
          id="filter-select"
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="filter-select"
        >
          <option value="all">All Types</option>
          <option value="communication">Communication</option>
          <option value="navigation">Navigation</option>
          <option value="weather">Weather</option>
          <option value="scientific">Scientific</option>
        </select>
      </div>

      {/* Satellite list */}
      <div className="satellite-list">
        {filteredSatellites.length === 0 ? (
          <p className="no-results">No satellites found</p>
        ) : (
          filteredSatellites.map(satellite => (
            <div
              key={satellite.id}
              className="satellite-item"
              onClick={() => onSatelliteSelect(satellite)}
            >
              <div className="satellite-item-name">{satellite.name}</div>
              <div className="satellite-item-norad">ID: {satellite.norad_id}</div>
            </div>
          ))
        )}
      </div>

      {/* Stats */}
      <div className="sidebar-stats">
        <div className="stat-item">
          <span className="stat-label">Total:</span>
          <span className="stat-value">{satellites.length}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Filtered:</span>
          <span className="stat-value">{filteredSatellites.length}</span>
        </div>
      </div>
    </div>
  );
}
