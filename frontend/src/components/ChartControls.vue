<template>
  <el-card shadow="never" class="chart-controls-card">
    <template #header>
      <span>
        <el-icon><Setting /></el-icon>
        Display Options
      </span>
    </template>
    
    <el-space wrap :size="15">
      <el-checkbox
        v-model="localOptions.showSurface"
        @change="updateOptions"
        border
      >
        <el-icon><Grid /></el-icon>
        Show Surface Atoms
      </el-checkbox>
      
      <el-checkbox
        v-model="localOptions.showSites"
        @change="updateOptions"
        border
      >
        <el-icon><Location /></el-icon>
        Show Adsorption Sites
      </el-checkbox>
      
      <el-checkbox
        v-model="localOptions.colorByEnergy"
        @change="updateOptions"
        border
      >
        <el-icon><Orange /></el-icon>
        Color by Energy
      </el-checkbox>
    </el-space>
  </el-card>
</template>

<script>
import { Setting, Grid, Location, Orange } from '@element-plus/icons-vue'

export default {
  name: 'ChartControls',
  components: {
    Setting,
    Grid,
    Location,
    Orange
  },
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
.chart-controls-card {
  margin-bottom: 15px;
}

:deep(.el-checkbox) {
  margin-right: 0;
}
</style>
