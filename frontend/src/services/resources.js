import api from './api'

export const authApi = {
  login: (email, password) => api.post('/api/auth/login', { email, password }),
  register: (data) => api.post('/api/auth/register', data),
  me: () => api.get('/api/auth/me'),
}

export const dashboardApi = {
  get: () => api.get('/api/dashboard'),
}

export const employeesApi = {
  list: (params) => api.get('/api/employees', { params }),
  get: (id) => api.get(`/api/employees/${id}`),
  create: (data) => api.post('/api/employees', data),
  update: (id, data) => api.put(`/api/employees/${id}`, data),
  deactivate: (id) => api.delete(`/api/employees/${id}`),
}

export const coursesApi = {
  list: (params) => api.get('/api/courses', { params }),
  myEnrollments: () => api.get('/api/courses/enrollments/me'),
  get: (id) => api.get(`/api/courses/${id}`),
  enroll: (id) => api.post(`/api/courses/${id}/enroll`),
  markVideoWatched: (courseId, videoId) => api.post(`/api/courses/${courseId}/videos/${videoId}/watched`),
  getQuiz: (id) => api.get(`/api/courses/${id}/quiz`),
  submitQuiz: (id, answers) => api.post(`/api/courses/${id}/quiz`, { answers }),
  complete: (id) => api.post(`/api/courses/${id}/complete`),
  create: (data) => api.post('/api/courses', data),
  update: (id, data) => api.put(`/api/courses/${id}`, data),
  deactivate: (id) => api.delete(`/api/courses/${id}`),
}

export const learningApi = {
  list: () => api.get('/api/learning'),
  create: (data) => api.post('/api/learning', data),
  byEmployee: (employeeId) => api.get(`/api/learning/employee/${employeeId}`),
  createForMe: (data) => api.post('/api/learning/me', data),
}

export const certificatesApi = {
  list: (params) => api.get('/api/certificates', { params }),
  get: (id) => api.get(`/api/certificates/${id}`),
  downloadUrl: (id) => {
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    return `${API_URL}/api/certificates/${id}/download`
  },
  download: (id) => api.get(`/api/certificates/${id}/download`, { responseType: 'blob' }),
  generate: (employeeId) => api.post(`/api/certificates/generate/${employeeId}`),
  resend: (id) => api.post(`/api/certificates/${id}/resend`),
}

export const automationApi = {
  run: () => api.post('/api/automation/run'),
  status: () => api.get('/api/automation/status'),
}

export const settingsApi = {
  get: () => api.get('/api/settings'),
  update: (data) => api.put('/api/settings', data),
}
