import * as THREE from 'three';

const EARTH_RADIUS_KM = 6371;
const SCALE = 0.0003;

/**
 * Convert ECEF (Earth-Centered, Earth-Fixed) coordinates to Three.js coordinate system
 * @param {Object} ecef - {x, y, z} in kilometers
 * @param {number} scale - Scale factor (default 0.001 for visualization)
 * @returns {THREE.Vector3}
 */
export function ecefToThree(ecef, scale = 0.0003) {
  return new THREE.Vector3(
    ecef.x * scale,
    ecef.z * scale,  // Swap Y and Z for Three.js coordinate system
    -ecef.y * scale
  );
}

/**
 * Convert Three.js coordinates to ECEF
 * @param {THREE.Vector3} threeCoords
 * @param {number} scale - Scale factor (default 0.001)
 * @returns {Object} {x, y, z} in kilometers
 */
export function threeToEcef(threeCoords, scale = 0.0003) {
  return {
    x: threeCoords.x / scale,
    y: -threeCoords.z / scale,
    z: threeCoords.y / scale,
  };
}

/**
 * Convert geodetic coordinates (lat, lon, alt) to ECEF
 * @param {number} latitude - in degrees
 * @param {number} longitude - in degrees
 * @param {number} altitude - in kilometers
 * @returns {Object} {x, y, z} in kilometers
 */
export function geodeticToEcef(latitude, longitude, altitude) {
  const EARTH_RADIUS_KM = 6371;

  const lat = (latitude * Math.PI) / 180;
  const lon = (longitude * Math.PI) / 180;
  const alt = altitude || 0;
  const r = EARTH_RADIUS_KM + alt;

  const x = r * Math.cos(lat) * Math.cos(lon);
  const y = r * Math.cos(lat) * Math.sin(lon);
  const z = r * Math.sin(lat);

  return { x, y, z };
}

/**
 * Convert ECEF to geodetic coordinates
 * @param {Object} ecef - {x, y, z} in kilometers
 * @returns {Object} {latitude, longitude, altitude}
 */
export function ecefToGeodetic(ecef) {
  const EARTH_RADIUS_KM = 6371;

  const r = Math.sqrt(ecef.x ** 2 + ecef.y ** 2 + ecef.z ** 2);
  const altitude = r - EARTH_RADIUS_KM;

  const latitude = Math.asin(ecef.z / r) * (180 / Math.PI);
  const longitude = Math.atan2(ecef.y, ecef.x) * (180 / Math.PI);

  return { latitude, longitude, altitude };
}

/**
 * Calculate scale factor based on zoom level
 * @param {number} zoom - Camera zoom level
 * @returns {number} Scale factor
 */
export function calculateScale(zoom) {
  // Adjust scale based on zoom for better visualization
  const baseScale = 0.0003;
  return baseScale * Math.pow(1.1, zoom);
}


/**
 * Переводит Широту, Долготу и Высоту (LLA) в декартовы координаты Three.js
 * с учетом сдвига осей (Y - вверх, Z - на зрителя) и масштаба сцены.
 */
export function llaToThree(lat, lon, alt) {
  // Переводим градусы в радианы
  const radLat = (lat * Math.PI) / 180;
  const radLon = (lon * Math.PI) / 180;

  // Полное расстояние от центра Земли до спутника с учетом масштаба
  const r = (EARTH_RADIUS_KM + alt) * SCALE;

  // Математическая проекция на сферы с выравниванием под ваши оси (X, Z, -Y из ECEF)
  const x = r * Math.cos(radLat) * Math.cos(radLon);
  const y = r * Math.sin(radLat);                       // Широта задает высоту по оси Y (Север)
  const z = -r * Math.cos(radLat) * Math.sin(radLon);    // Долгота проецируется на плоскость XZ

  return [x, y, z];
}