<template>
  <el-card shadow="never" class="mesh-controls-card">
    <template #header>
      <span>
        <el-icon><Tools /></el-icon>
        Mesh Display Controls
      </span>
    </template>
    
    <el-form label-position="left" label-width="140px" size="small">
      <el-form-item label="Display Mode">
        <el-radio-group v-model="localOptions.wireframe" @change="emitUpdate">
          <el-radio-button :label="false">Solid</el-radio-button>
          <el-radio-button :label="true">Wireframe</el-radio-button>
        </el-radio-group>
      </el-form-item>
      
      <el-form-item label="Opacity">
        <el-slider
          v-model="localOptions.opacity"
          :min="0.1"
          :max="1.0"
          :step="0.1"
          @change="emitUpdate"
          show-input
        />
      </el-form-item>
      
      <el-form-item label="Color Scheme">
        <el-select v-model="localOptions.colorScheme" @change="emitUpdate" placeholder="Select scheme">
          <el-option label="Viridis (Green-Yellow-Red)" value="viridis" />
          <el-option label="Cool (Blue-Cyan)" value="cool" />
          <el-option label="Hot (Red-Orange-Yellow)" value="hot" />
        </el-select>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script>
import { Tools } from '@element-plus/icons-vue'

export default {
  name: 'MeshControls',
  components: {
    Tools
  },
  props: {
    options: {
      type: Object,
      default: () => ({
        wireframe: false,
        opacity: 1.0,
        colorScheme: 'viridis'
      })
    }
  },
  data() {
    return {
      localOptions: { ...this.options }
    }
  },
  watch: {
    options: {
      deep: true,
      handler(newVal) {
        this.localOptions = { ...newVal }
      }
    }
  },
  methods: {
    emitUpdate() {
      this.$emit('update-options', this.localOptions)
    }
  }
}
</script>

<style scoped>
.mesh-controls-card {
  margin-bottom: 15px;
}
</style>
