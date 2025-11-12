<template>
  <div class="visualization-chart">
    <el-tabs v-model="activeTab" type="border-card">
      <el-tab-pane name="scatter">
        <template #label>
          <span>
            <el-icon><Histogram /></el-icon>
            Scatter Plot
          </span>
        </template>
        
        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="8" animated />
        </div>
        <div v-else-if="error">
          <el-alert
            :title="error"
            type="error"
            :closable="false"
            show-icon
          />
        </div>
        <div v-else ref="plotContainer" class="plot-container"></div>
      </el-tab-pane>
      
      <el-tab-pane name="heatmap">
        <template #label>
          <span>
            <el-icon><TrendCharts /></el-icon>
            Heat Map
          </span>
        </template>
        
        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="8" animated />
        </div>
        <div v-else-if="error">
          <el-alert
            :title="error"
            type="error"
            :closable="false"
            show-icon
          />
        </div>
        <div v-else ref="heatmapContainer" class="plot-container"></div>
      </el-tab-pane>
      
      <el-tab-pane name="mesh">
        <template #label>
          <span>
            <el-icon><Grid /></el-icon>
            Surface Mesh
          </span>
        </template>
        
        <MeshControls :options="meshOptions" @update-options="handleMeshOptionsUpdate" />
        <SurfaceMeshViewer 
          v-if="sessionId"
          :session-id="sessionId"
          :mesh-options="meshOptions"
        />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import { Histogram, TrendCharts, Grid } from '@element-plus/icons-vue'
import Plotly from 'plotly.js-dist-min'
import api from '../services/api'
import SurfaceMeshViewer from './SurfaceMeshViewer.vue'
import MeshControls from './MeshControls.vue'

export default {
  name: 'VisualizationChart',
  components: {
    Histogram,
    TrendCharts,
    Grid,
    SurfaceMeshViewer,
    MeshControls
  },
  props: {
    sessionId: {
      type: String,
      required: true
    },
    displayOptions: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      activeTab: 'scatter',
      loading: false,
      error: null,
      surfaceData: null,
      sitesData: null,
      meshOptions: {
        wireframe: false,
        opacity: 1.0,
        colorScheme: 'viridis'
      }
    }
  },
  watch: {
    sessionId: {
      immediate: true,
      handler() {
        this.loadData()
      }
    },
    displayOptions: {
      deep: true,
      handler() {
        this.updatePlots()
      }
    },
    activeTab(newTab) {
      this.$nextTick(() => {
        if (newTab === 'scatter') {
          this.updateScatterPlot()
        } else if (newTab === 'heatmap') {
          this.updateHeatmap()
        }
      })
    }
  },
  methods: {
    async loadData() {
      this.loading = true
      this.error = null
      
      try {
        const [surface, sites] = await Promise.all([
          api.getVizData(this.sessionId, 'surface_atoms.json').catch(() => ({ coords: [] })),
          api.getVizData(this.sessionId, 'adsorption_sites.json')
        ])
        
        this.surfaceData = surface
        this.sitesData = sites
        this.updatePlots()
      } catch (error) {
        this.error = 'Failed to load visualization data'
        console.error(error)
      } finally {
        this.loading = false
      }
    },
    
    updatePlots() {
      this.$nextTick(() => {
        if (this.activeTab === 'scatter') {
          this.updateScatterPlot()
        } else if (this.activeTab === 'heatmap') {
          this.updateHeatmap()
        }
      })
    },
    
    updateScatterPlot() {
      if (!this.sitesData || !this.$refs.plotContainer) return
      
      const traces = []
      
      // Surface atoms trace
      if (this.displayOptions.showSurface && this.surfaceData?.coords) {
        const coords = this.surfaceData.coords
        traces.push({
          type: 'scatter3d',
          mode: 'markers',
          x: coords.map(c => c[0]),
          y: coords.map(c => c[1]),
          z: coords.map(c => c[2]),
          marker: {
            size: 3,
            color: '#909399',
            opacity: 0.5
          },
          name: 'Surface Atoms',
          hoverinfo: 'x+y+z'
        })
      }
      
      // Adsorption sites trace
      if (this.displayOptions.showSites && this.sitesData?.sites) {
        const sites = this.sitesData.sites
        const energies = sites.map(s => s.energy)
        const minEnergy = Math.min(...energies)
        const maxEnergy = Math.max(...energies)
        
        traces.push({
          type: 'scatter3d',
          mode: 'markers',
          // Support both 'position' (new) and 'coords' (legacy) data formats
          x: sites.map(s => (s.position || s.coords)?.[0]),
          y: sites.map(s => (s.position || s.coords)?.[1]),
          z: sites.map(s => (s.position || s.coords)?.[2]),
          marker: {
            size: 6,
            color: this.displayOptions.colorByEnergy ? energies : '#409EFF',
            colorscale: this.displayOptions.colorByEnergy ? 'Viridis' : undefined,
            colorbar: this.displayOptions.colorByEnergy ? {
              title: 'Energy (eV)',
              thickness: 15,
              len: 0.7
            } : undefined,
            cmin: minEnergy,
            cmax: maxEnergy,
            opacity: 0.8
          },
          text: sites.map(s => `Energy: ${s.energy?.toFixed(3) || 'N/A'} eV<br>Type: ${s.type}`),
          hoverinfo: 'text+x+y+z',
          name: 'Adsorption Sites'
        })
      }
      
      const layout = {
        scene: {
          xaxis: { title: 'X (Å)' },
          yaxis: { title: 'Y (Å)' },
          zaxis: { title: 'Z (Å)' },
          camera: {
            eye: { x: 1.5, y: 1.5, z: 1.5 }
          }
        },
        margin: { l: 0, r: 0, t: 0, b: 0 },
        showlegend: true,
        legend: {
          x: 0,
          y: 1
        },
        hovermode: 'closest'
      }
      
      const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false
      }
      
      Plotly.newPlot(this.$refs.plotContainer, traces, layout, config)
    },
    
    updateHeatmap() {
      if (!this.sitesData || !this.$refs.heatmapContainer) return
      
      const sites = this.sitesData.sites || []
      if (sites.length === 0) return
      
      // Create 2D heatmap projection
      // Support both 'position' (new) and 'coords' (legacy) data formats
      const x = sites.map(s => (s.position || s.coords)?.[0])
      const y = sites.map(s => (s.position || s.coords)?.[1])
      const z = sites.map(s => s.energy)
      
      const trace = {
        type: 'scatter',
        mode: 'markers',
        x: x,
        y: y,
        marker: {
          size: 12,
          color: z,
          colorscale: 'Viridis',
          colorbar: {
            title: 'Energy (eV)',
            thickness: 15
          },
          showscale: true
        },
        text: sites.map(s => `Energy: ${s.energy?.toFixed(3) || 'N/A'} eV`),
        hoverinfo: 'text+x+y',
        name: 'Adsorption Sites'
      }
      
      const layout = {
        xaxis: { title: 'X (Å)' },
        yaxis: { title: 'Y (Å)' },
        margin: { l: 60, r: 50, t: 40, b: 60 },
        hovermode: 'closest',
        title: 'Adsorption Energy Heatmap (Top View)'
      }
      
      const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false
      }
      
      Plotly.newPlot(this.$refs.heatmapContainer, [trace], layout, config)
    },
    
    handleMeshOptionsUpdate(options) {
      this.meshOptions = { ...options }
    }
  }
}
</script>

<style scoped>
.visualization-chart {
  width: 100%;
}

.plot-container {
  width: 100%;
  height: 600px;
  background: white;
  border-radius: 4px;
}

.loading-container {
  padding: 20px;
}

:deep(.el-tabs__content) {
  padding: 15px;
}

:deep(.el-tabs__item) {
  font-weight: 500;
}
</style>
