<template>
  <div class="dashboard">
    <el-row :gutter="20" class="dashboard-row">
      <!-- Calculation Form -->
      <el-col :xs="24" :lg="12">
        <CalculationForm 
          @calculation-started="handleCalculationStarted"
          :is-running="isCalculationRunning"
        />
      </el-col>
      
      <!-- Results and Visualization -->
      <el-col :xs="24" :lg="12">
        <!-- Progress and Status -->
        <el-card v-if="currentSessionId" shadow="hover" class="status-card">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><Document /></el-icon>
                Calculation Progress
              </span>
              <el-tag :type="statusTagType">{{ statusText }}</el-tag>
            </div>
          </template>
          
          <el-progress 
            v-if="!calculationComplete"
            :percentage="50" 
            :indeterminate="true"
            :duration="3"
            status="success"
          />
          
          <el-alert
            v-if="calculationComplete"
            title="Calculation Complete!"
            type="success"
            :closable="false"
            show-icon
          />
          
          <div class="log-container" ref="logContainer">
            <div v-for="(log, index) in logs" :key="index" class="log-line">
              {{ log }}
            </div>
          </div>
        </el-card>
        
        <!-- Visualization -->
        <el-card v-if="currentSessionId && calculationComplete" shadow="hover" class="viz-card">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><TrendCharts /></el-icon>
                Visualization Results
              </span>
            </div>
          </template>
          <ChartControls @update-display="handleUpdateDisplay" />
          <VisualizationChart 
            :session-id="currentSessionId"
            :display-options="displayOptions"
          />
        </el-card>
      </el-col>
    </el-row>
    
    <!-- Result History -->
    <ResultHistory :results="results" @load-result="handleLoadResult" />
  </div>
</template>

<script>
import { Document, TrendCharts } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
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
    ResultHistory,
    Document,
    TrendCharts
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
    },
    statusTagType() {
      if (this.calculationComplete) return 'success'
      if (this.currentSessionId) return 'warning'
      return 'info'
    }
  },
  methods: {
    async handleCalculationStarted(sessionData) {
      this.currentSessionId = sessionData.session_id
      this.logs = []
      this.calculationComplete = false
      
      this.$emit('start-calculation', sessionData)
      
      ElMessage.success('Calculation started successfully!')
      
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
            ElMessage.success('Calculation completed!')
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
        ElMessage.error('Failed to load results')
      }
    },
    
    handleLoadResult(result) {
      this.currentSessionId = result.session_id
      this.calculationComplete = true
      this.logs = ['[SYSTEM] Loaded historical result']
      ElMessage.info('Loaded historical calculation result')
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
.dashboard-row {
  margin-bottom: 20px;
}

.status-card,
.viz-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.card-header span {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.log-container {
  background: #1e1e1e;
  color: #d4d4d4;
  font-family: 'Courier New', 'Consolas', monospace;
  font-size: 0.875rem;
  padding: 1rem;
  border-radius: 4px;
  height: 350px;
  overflow-y: auto;
  margin-top: 1rem;
  line-height: 1.5;
}

.log-line {
  padding: 2px 0;
  white-space: pre-wrap;
  word-break: break-all;
}

@media (max-width: 992px) {
  .dashboard-row {
    flex-direction: column;
  }
}
</style>
