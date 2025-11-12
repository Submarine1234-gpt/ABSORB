<template>
  <div class="visualization-chart">
    <h3 class="card-title">3D Visualization</h3>
    <div v-if="loading" class="loading">Loading visualization data...</div>
    <div v-else-if="error" class="alert alert-error">{{ error }}</div>
    <div v-else ref="plotContainer" class="plot-container"></div>
  </div>
</template>

<script>
import Plotly from 'plotly.js-dist-min'
import api from '../services/api'

export default {
  name: 'VisualizationChart',
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
      loading: false,
      error: null,
      surfaceData: null,
      sitesData: null
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
        this.updatePlot()
      }
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
        this.updatePlot()
      } catch (error) {
        this.error = 'Failed to load visualization data'
        console.error(error)
      } finally {
        this.loading = false
      }
    },
    
    updatePlot() {
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
            color: '#999',
            opacity: 0.5
          },
          name: 'Surface Atoms'
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
          x: sites.map(s => s.coords[0]),
          y: sites.map(s => s.coords[1]),
          z: sites.map(s => s.coords[2]),
          marker: {
            size: 8,
            color: this.displayOptions.colorByEnergy ? energies : '#667eea',
            colorscale: 'Viridis',
            showscale: this.displayOptions.colorByEnergy,
            colorbar: {
              title: 'Energy (eV)',
              x: 1.1
            },
            cmin: minEnergy,
            cmax: maxEnergy
          },
          text: sites.map(s => `Energy: ${s.energy.toFixed(4)} eV`),
          hoverinfo: 'text',
          name: 'Adsorption Sites'
        })
      }
      
      const layout = {
        scene: {
          xaxis: { title: 'X (Å)' },
          yaxis: { title: 'Y (Å)' },
          zaxis: { title: 'Z (Å)' },
          aspectmode: 'data'
        },
        margin: { l: 0, r: 0, t: 0, b: 0 },
        showlegend: true,
        legend: { x: 0, y: 1 }
      }
      
      const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['toImage']
      }
      
      Plotly.newPlot(this.$refs.plotContainer, traces, layout, config)
    }
  }
}
</script>

<style scoped>
.plot-container {
  width: 100%;
  height: 600px;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #666;
}
</style>
