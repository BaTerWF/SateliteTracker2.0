import apiClient from './client';

export const satellitesAPI = {
  // Get all satellites
  getAll: () => apiClient.get('/api/v1/satellites/'),

  // Get single satellite
  getById: (id) => apiClient.get(`/api/v1/satellites/${id}`),

  // Get satellite position
  getPosition: (id) => apiClient.get(`/api/v1/satellites/${id}/position`),

  getOrbit: (id) => apiClient.get(`/api/v1/satellites/${id}/orbit`),

  // Create satellite
  create: (data) => apiClient.post('/api/v1/satellites', data),

  // Update satellite
  update: (id, data) => apiClient.put(`/api/v1/satellites/${id}`, data),

  // Delete satellite
  delete: (id) => apiClient.delete(`/api/v1/satellites/${id}`),
};
