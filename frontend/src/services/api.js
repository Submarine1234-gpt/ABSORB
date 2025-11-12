/**
 * API service for communicating with backend
 */
import axios from 'axios'
import { API_BASE_URL } from '../utils/constants'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for long calculations
  headers: {
    'Content-Type': 'application/json'
  }
})

export default {
  /**
   * Submit a new calculation
   * @param {FormData} formData - Form data with files and parameters
   * @returns {Promise} Response with session_id
   */
  async submitCalculation(formData) {
    const response = await api.post('/run-calculation', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  /**
   * Check calculation status
   * @param {string} sessionId - Session identifier
   * @returns {Promise} Status object
   */
  async checkStatus(sessionId) {
    const response = await api.get(`/check-status/${sessionId}`)
    return response.data
  },

  /**
   * Get visualization data
   * @param {string} sessionId - Session identifier
   * @param {string} filename - Data filename
   * @returns {Promise} Visualization data
   */
  async getVizData(sessionId, filename) {
    const response = await api.get(`/get-viz-data/${sessionId}/${filename}`)
    return response.data
  },

  /**
   * Get all calculation results
   * @returns {Promise} Array of results
   */
  async getResults() {
    const response = await api.get('/get-results')
    return response.data
  },

  /**
   * Get download URL for results
   * @param {string} sessionId - Session identifier
   * @returns {string} Download URL
   */
  getDownloadUrl(sessionId) {
    return `${API_BASE_URL}/download-result/${sessionId}`
  },

  /**
   * Get log stream URL
   * @param {string} sessionId - Session identifier
   * @returns {string} Log stream URL
   */
  getLogStreamUrl(sessionId) {
    return `${API_BASE_URL}/stream-logs/${sessionId}`
  },

  /**
   * Check API health
   * @returns {Promise} Health status
   */
  async checkHealth() {
    const response = await api.get('/api/health')
    return response.data
  }
}
