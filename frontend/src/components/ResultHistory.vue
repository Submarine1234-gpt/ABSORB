<template>
  <div class="card">
    <h2 class="card-title">Calculation History</h2>
    
    <div v-if="results.length === 0" class="empty-state">
      No calculations yet. Start your first calculation above!
    </div>
    
    <div v-else class="results-table-container">
      <table class="results-table">
        <thead>
          <tr>
            <th>Date/Time</th>
            <th>Session ID</th>
            <th>Surface Axis</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="result in results" :key="result.session_id">
            <td>{{ result.timestamp }}</td>
            <td class="session-id">{{ result.session_id.substring(0, 8) }}...</td>
            <td>{{ getSurfaceAxisLabel(result.surface_axis) }}</td>
            <td class="actions">
              <button 
                @click="loadResult(result)" 
                class="btn btn-secondary btn-sm"
              >
                View
              </button>
              <a 
                :href="getDownloadUrl(result.session_id)" 
                class="btn btn-secondary btn-sm"
                download
              >
                Download
              </a>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'ResultHistory',
  props: {
    results: {
      type: Array,
      default: () => []
    }
  },
  methods: {
    getSurfaceAxisLabel(axis) {
      const labels = ['X (0)', 'Y (1)', 'Z (2)']
      return labels[axis] || axis
    },
    
    getDownloadUrl(sessionId) {
      return api.getDownloadUrl(sessionId)
    },
    
    loadResult(result) {
      this.$emit('load-result', result)
    }
  }
}
</script>

<style scoped>
.empty-state {
  text-align: center;
  padding: 3rem;
  color: #999;
  font-style: italic;
}

.results-table-container {
  overflow-x: auto;
}

.results-table {
  width: 100%;
  border-collapse: collapse;
}

.results-table th,
.results-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.results-table th {
  background: #f5f5f5;
  font-weight: 600;
  color: #555;
}

.results-table tbody tr:hover {
  background: #f9f9f9;
}

.session-id {
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.btn-sm {
  padding: 0.4rem 0.8rem;
  font-size: 0.9rem;
}
</style>
