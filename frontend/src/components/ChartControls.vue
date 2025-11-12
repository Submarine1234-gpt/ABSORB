<template>
  <div class="chart-controls">
    <h3>Display Options</h3>
    <div class="controls-grid">
      <label class="checkbox-group">
        <input type="checkbox" v-model="localOptions.showSurface" @change="updateOptions" />
        <span>Show Surface Atoms</span>
      </label>
      
      <label class="checkbox-group">
        <input type="checkbox" v-model="localOptions.showSites" @change="updateOptions" />
        <span>Show Adsorption Sites</span>
      </label>
      
      <label class="checkbox-group">
        <input type="checkbox" v-model="localOptions.colorByEnergy" @change="updateOptions" />
        <span>Color by Energy</span>
      </label>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ChartControls',
  data() {
    return {
      localOptions: {
        showSurface: true,
        showSites: true,
        colorByEnergy: true
      }
    }
  },
  methods: {
    updateOptions() {
      this.$emit('update-display', this.localOptions)
    }
  }
}
</script>

<style scoped>
.chart-controls {
  margin-bottom: 1rem;
  padding: 1rem;
  background: #f5f5f5;
  border-radius: 5px;
}

.chart-controls h3 {
  font-size: 1rem;
  margin-bottom: 0.75rem;
  color: #555;
}

.controls-grid {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}
</style>
