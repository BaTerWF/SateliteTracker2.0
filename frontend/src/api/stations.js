import apiClient from './client';

export const stationsAPI = {
  // Get all ground stations
  getAll: () => apiClient.get('/api/v1/stations/'),

  // Get single station
  getById: (id) => apiClient.get(`/api/v1/stations/${id}/`),

  // Get visible satellites for a station
  getVisibleSatellites: (id) => apiClient.get(`/api/v1/stations/${id}/visible_satellites/`),

  // Create station
  create: (data) => apiClient.post('/api/v1/stations/', data),

  // Update station
  update: (id, data) => apiClient.put(`/api/v1/stations/${id}/`, data),

  // Delete station
  delete: (id) => apiClient.delete(`/api/v1/stations/${id}/`),
};
