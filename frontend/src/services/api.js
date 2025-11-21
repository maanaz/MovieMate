import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Content API
export const contentAPI = {
  getAll: (params) => api.get('/content/', { params }),
  get: (id) => api.get(`/content/${id}/`),
  create: (data) => api.post('/content/', data),
  update: (id, data) => api.patch(`/content/${id}/`, data),
  delete: (id) => api.delete(`/content/${id}/`),
  getMovies: () => api.get('/content/movies/'),
  getTVShows: () => api.get('/content/tv_shows/'),
  getStatistics: () => api.get('/content/statistics/'),
  getRecommendations: () => api.get('/content/recommendations/'),
  searchTMDB: (query, type) => api.get('/content/search_tmdb/', { params: { q: query, type } }),
  importFromTMDB: (data) => api.post('/content/import_from_tmdb/', data),
  searchOMDB: (query, type) => api.get('/content/search_omdb/', { params: { q: query, type } }),
  importFromOMDB: (data) => api.post('/content/import_from_omdb/', data),
  getCompletionEstimate: (id) => api.get(`/content/${id}/completion_estimate/`),
}

// Genre API
export const genreAPI = {
  getAll: () => api.get('/genres/'),
  create: (data) => api.post('/genres/', data),
}

// Platform API
export const platformAPI = {
  getAll: () => api.get('/platforms/'),
  create: (data) => api.post('/platforms/', data),
}

// Rating API
export const ratingAPI = {
  getAll: () => api.get('/ratings/'),
  create: (data) => api.post('/ratings/', data),
  update: (id, data) => api.put(`/ratings/${id}/`, data),
}

// Review API
export const reviewAPI = {
  getAll: () => api.get('/reviews/'),
  create: (data) => api.post('/reviews/', data),
  update: (id, data) => api.put(`/reviews/${id}/`, data),
  generateFromNotes: (data) => api.post('/reviews/generate_from_notes/', data),
}

// Watch Progress API
export const watchProgressAPI = {
  getAll: () => api.get('/watch-progress/'),
  create: (data) => api.post('/watch-progress/', data),
  markEpisode: (data) => api.post('/watch-progress/mark_episode/', data),
}

// Watch History API
export const watchHistoryAPI = {
  getAll: () => api.get('/watch-history/'),
  getStatistics: () => api.get('/watch-history/statistics/'),
}

export default api


