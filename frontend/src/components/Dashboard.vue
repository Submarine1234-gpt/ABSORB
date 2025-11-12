<template>
  <div class="dashboard">
    <div class="dashboard-grid">
      <!-- Calculation Form -->
      <div class="dashboard-col">
        <CalculationForm 
          @calculation-started="handleCalculationStarted"
          :is-running="isCalculationRunning"
        />
      </div>
      
      <!-- Results and Visualization -->
      <div class="dashboard-col">
        <!-- Logs Section -->
        <div v-if="currentSessionId" class="card">
          <h2 class="card-title">Calculation Logs</h2>
          <div class="log-container" ref="logContainer">
            <div v-for="(log, index) in logs" :key="index" class="log-line">
              {{ log }}
            </div>
          </div>
          <div class="status-bar">
            <span :class="['status-indicator', statusClass]">
              {{ statusText }}
            </span>
          </div>
        </div>
        
        <!-- Visualization -->
        <div v-if="currentSessionId && calculationComplete" class="card">
          <ChartControls @update-display="handleUpdateDisplay" />
          <VisualizationChart 
            :session-id="currentSessionId"
            :display-options="displayOptions"
          />
        </div>
      </div>
    </div>
    
    <!-- Result History -->
    <ResultHistory :results="results" @load-result="handleLoadResult" />
  </div>
</template>

<script>
import CalculationForm from './CalculationForm.vue'
import ChartControls from './ChartControls.vue'
import VisualizationChart from './VisualizationChart.vue'
import ResultHistory from './ResultHistory.vue'
import api from '../services/api'

export default {
  name: 'Dashboard',
  components: {
    CalculationForm,
    ChartControls,
    VisualizationChart,
    ResultHistory
  },
  data() {
    return {
      currentSessionId: null,
      logs: [],
      calculationComplete: false,
      displayOptions: {
        showSurface: true,
        showSites: true,
        colorByEnergy: true
      },
      results: [],
      eventSource: null,
      statusCheckInterval: null
    }
  },
  computed: {
    isCalculationRunning() {
      return this.currentSessionId && !this.calculationComplete
    },
    statusClass() {
      if (this.calculationComplete) return 'status-complete'
      if (this.currentSessionId) return 'status-running'
      return 'status-idle'
    },
    statusText() {
      if (this.calculationComplete) return 'Complete'
      if (this.currentSessionId) return 'Running...'
      return 'Idle'
    }
  },
  methods: {
    async handleCalculationStarted(sessionData) {
      this.currentSessionId = sessionData.session_id
      this.logs = []
      this.calculationComplete = false
      
      this.$emit('start-calculation', sessionData)
      
      // Start log streaming
      this.startLogStreaming()
      
      // Start status checking
      this.startStatusCheck()
    },
    
    startLogStreaming() {
      if (this.eventSource) {
        this.eventSource.close()
      }
      
      const url = api.getLogStreamUrl(this.currentSessionId)
      this.eventSource = new EventSource(url)
      
      this.eventSource.onmessage = (event) => {
        this.logs.push(event.data)
        this.$nextTick(() => {
          this.scrollLogsToBottom()
        })
      }
      
      this.eventSource.onerror = () => {
        this.eventSource.close()
      }
    },
    
    async startStatusCheck() {
      this.statusCheckInterval = setInterval(async () => {
        try {
          const status = await api.checkStatus(this.currentSessionId)
          if (status.status === 'complete') {
            this.calculationComplete = true
            this.stopStatusCheck()
            await this.loadResults()
          }
        } catch (error) {
          console.error('Status check failed:', error)
        }
      }, 2000)
    },
    
    stopStatusCheck() {
      if (this.statusCheckInterval) {
        clearInterval(this.statusCheckInterval)
        this.statusCheckInterval = null
      }
      if (this.eventSource) {
        this.eventSource.close()
        this.eventSource = null
      }
    },
    
    scrollLogsToBottom() {
      const container = this.$refs.logContainer
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    },
    
    handleUpdateDisplay(options) {
      this.displayOptions = { ...this.displayOptions, ...options }
    },
    
    async loadResults() {
      try {
        this.results = await api.getResults()
      } catch (error) {
        console.error('Failed to load results:', error)
      }
    },
    
    handleLoadResult(result) {
      this.currentSessionId = result.session_id
      this.calculationComplete = true
      this.logs = ['[SYSTEM] Loaded historical result']
    }
  },
  mounted() {
    this.loadResults()
  },
  beforeUnmount() {
    this.stopStatusCheck()
  }
}
</script>

<style scoped>
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

@media (max-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

.log-container {
  background: #1e1e1e;
  color: #d4d4d4;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  padding: 1rem;
  border-radius: 5px;
  height: 400px;
  overflow-y: auto;
  margin-bottom: 1rem;
}

.log-line {
  padding: 2px 0;
  white-space: pre-wrap;
  word-break: break-all;
}

.status-bar {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.status-indicator {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 500;
  font-size: 0.9rem;
}

.status-idle {
  background: #e0e0e0;
  color: #666;
}

.status-running {
  background: #fff3e0;
  color: #f57c00;
  animation: pulse 2s infinite;
}

.status-complete {
  background: #e8f5e9;
  color: #388e3c;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
</style>
