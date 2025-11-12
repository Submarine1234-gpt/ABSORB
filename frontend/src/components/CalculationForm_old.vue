<template>
  <div class="card">
    <h2 class="card-title">New Calculation</h2>
    
    <div v-if="errorMessage" class="alert alert-error">
      {{ errorMessage }}
    </div>
    
    <form @submit.prevent="submitCalculation">
      <!-- File Uploads -->
      <div class="form-section">
        <h3>Input Files</h3>
        
        <div class="form-group">
          <label for="substrate">Substrate CIF File *</label>
          <input 
            type="file" 
            id="substrate" 
            accept=".cif"
            @change="handleFileChange('substrate', $event)"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="adsorbate">Adsorbate CIF File *</label>
          <input 
            type="file" 
            id="adsorbate" 
            accept=".cif"
            @change="handleFileChange('adsorbate', $event)"
            required
          />
        </div>
      </div>
      
      <!-- Basic Parameters -->
      <div class="form-section">
        <h3>Basic Parameters</h3>
        
        <div class="form-group">
          <label for="surface_axis">Surface Axis</label>
          <select v-model.number="params.surface_axis" id="surface_axis">
            <option :value="0">X-axis (0)</option>
            <option :value="1">Y-axis (1)</option>
            <option :value="2">Z-axis (2)</option>
          </select>
        </div>
        
        <div class="form-group checkbox-group">
          <input 
            type="checkbox" 
            v-model="params.place_on_bottom" 
            id="place_on_bottom"
          />
          <label for="place_on_bottom">Place on bottom surface</label>
        </div>
        
        <div class="form-group">
          <label for="adsorption_height">
            Adsorption Height (Å): {{ params.adsorption_height }}
          </label>
          <input 
            type="range" 
            v-model.number="params.adsorption_height"
            id="adsorption_height"
            min="0.1" 
            max="10" 
            step="0.1"
          />
        </div>
        
        <div class="form-group">
          <label for="vacuum_thickness">
            Vacuum Thickness (Å): {{ params.vacuum_thickness }}
          </label>
          <input 
            type="range" 
            v-model.number="params.vacuum_thickness"
            id="vacuum_thickness"
            min="5" 
            max="50" 
            step="1"
          />
        </div>
        
        <div class="form-group">
          <label for="collision_threshold">
            Collision Threshold (Å): {{ params.collision_threshold }}
          </label>
          <input 
            type="range" 
            v-model.number="params.collision_threshold"
            id="collision_threshold"
            min="0.5" 
            max="3" 
            step="0.1"
          />
        </div>
      </div>
      
      <!-- Site Detection -->
      <div class="form-section">
        <h3>Site Detection</h3>
        
        <div class="form-group checkbox-group">
          <input 
            type="checkbox" 
            v-model="params.hollow_sites_enabled" 
            id="hollow_sites_enabled"
          />
          <label for="hollow_sites_enabled">Enable hollow site detection</label>
        </div>
        
        <div v-if="params.hollow_sites_enabled" class="sub-params">
          <div class="form-group">
            <label for="knn_neighbors">
              KNN Neighbors: {{ params.knn_neighbors }}
            </label>
            <input 
              type="range" 
              v-model.number="params.knn_neighbors"
              id="knn_neighbors"
              min="1" 
              max="10" 
              step="1"
            />
          </div>
        </div>
        
        <div class="form-group checkbox-group">
          <input 
            type="checkbox" 
            v-model="params.on_top_sites_enabled" 
            id="on_top_sites_enabled"
          />
          <label for="on_top_sites_enabled">Enable on-top site detection</label>
        </div>
        
        <div v-if="params.on_top_sites_enabled" class="sub-params">
          <div class="form-group">
            <label for="on_top_target_atom">Target Atom</label>
            <input 
              type="text" 
              v-model="params.on_top_target_atom"
              id="on_top_target_atom"
              placeholder="e.g., O, C, N"
            />
          </div>
        </div>
      </div>
      
      <!-- Rotation Optimization -->
      <div class="form-section">
        <h3>Rotation Optimization</h3>
        
        <div class="form-group checkbox-group">
          <input 
            type="checkbox" 
            v-model="params.rotation_method" 
            id="rotation_method"
          />
          <label for="rotation_method">Use spherical sampling method</label>
        </div>
        
        <div v-if="params.rotation_method" class="sub-params">
          <div class="form-group">
            <label for="rotation_count">
              Rotation Count: {{ params.rotation_count }}
            </label>
            <input 
              type="range" 
              v-model.number="params.rotation_count"
              id="rotation_count"
              min="10" 
              max="200" 
              step="10"
            />
          </div>
          
          <div class="form-group">
            <label for="rotation_step">
              Rotation Step (degrees): {{ params.rotation_step }}
            </label>
            <input 
              type="range" 
              v-model.number="params.rotation_step"
              id="rotation_step"
              min="1" 
              max="90" 
              step="1"
            />
          </div>
        </div>
      </div>
      
      <!-- Submit Button -->
      <button 
        type="submit" 
        class="btn btn-primary" 
        :disabled="isRunning || !canSubmit"
        style="width: 100%;"
      >
        {{ isRunning ? 'Running...' : 'Start Calculation' }}
      </button>
    </form>
  </div>
</template>

<script>
import api from '../services/api'
import { DEFAULT_PARAMS } from '../utils/constants'

export default {
  name: 'CalculationForm',
  props: {
    isRunning: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      files: {
        substrate: null,
        adsorbate: null
      },
      params: { ...DEFAULT_PARAMS },
      errorMessage: ''
    }
  },
  computed: {
    canSubmit() {
      return this.files.substrate && this.files.adsorbate
    }
  },
  methods: {
    handleFileChange(type, event) {
      const file = event.target.files[0]
      if (file) {
        this.files[type] = file
      }
    },
    
    async submitCalculation() {
      this.errorMessage = ''
      
      try {
        // Create FormData
        const formData = new FormData()
        formData.append('substrate_file', this.files.substrate)
        formData.append('adsorbate_file', this.files.adsorbate)
        
        // Add all parameters
        for (const [key, value] of Object.entries(this.params)) {
          formData.append(key, value)
        }
        
        // Submit calculation
        const response = await api.submitCalculation(formData)
        
        if (response.success) {
          this.$emit('calculation-started', response)
        } else {
          this.errorMessage = response.message || 'Failed to start calculation'
        }
      } catch (error) {
        this.errorMessage = error.response?.data?.message || 'An error occurred'
        console.error('Calculation submission failed:', error)
      }
    }
  }
}
</script>

<style scoped>
.form-section {
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.form-section:last-of-type {
  border-bottom: none;
}

.form-section h3 {
  font-size: 1.1rem;
  margin-bottom: 1rem;
  color: #667eea;
}

.sub-params {
  margin-left: 1.5rem;
  padding-left: 1rem;
  border-left: 2px solid #e0e0e0;
}

input[type="range"] {
  width: 100%;
  cursor: pointer;
}

input[type="file"] {
  padding: 0.5rem;
}
</style>
