<template>
  <el-card shadow="hover" class="calculation-form-card">
    <template #header>
      <div class="card-header">
        <span>
          <el-icon><Edit /></el-icon>
          New Calculation
        </span>
      </div>
    </template>
    
    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="error"
      :closable="true"
      @close="errorMessage = ''"
      show-icon
    />
    
    <el-form
      ref="formRef"
      :model="formData"
      label-position="top"
      @submit.prevent="submitCalculation"
    >
      <!-- File Upload Section -->
      <el-collapse v-model="activeCollapse" accordion>
        <el-collapse-item title="Input Files" name="files">
          <template #title>
            <el-icon><Upload /></el-icon>
            <span style="margin-left: 8px;">Input Files</span>
            <el-tag v-if="filesUploaded" type="success" size="small" style="margin-left: 10px;">
              {{ uploadedFilesCount }} files
            </el-tag>
          </template>
          
          <el-form-item label="Substrate CIF File" required>
            <el-upload
              class="upload-demo"
              drag
              :auto-upload="false"
              :limit="1"
              accept=".cif"
              :on-change="(file) => handleFileChange('substrate', file)"
              :file-list="substrateFileList"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                Drop substrate CIF file here or <em>click to upload</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  CIF file format only
                </div>
              </template>
            </el-upload>
          </el-form-item>
          
          <el-form-item label="Adsorbate CIF File" required>
            <el-upload
              class="upload-demo"
              drag
              :auto-upload="false"
              :limit="1"
              accept=".cif"
              :on-change="(file) => handleFileChange('adsorbate', file)"
              :file-list="adsorbateFileList"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                Drop adsorbate CIF file here or <em>click to upload</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  CIF file format only
                </div>
              </template>
            </el-upload>
          </el-form-item>
        </el-collapse-item>
        
        <!-- Basic Parameters -->
        <el-collapse-item title="Basic Parameters" name="basic">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span style="margin-left: 8px;">Basic Parameters</span>
          </template>
          
          <el-form-item label="Surface Axis">
            <el-select v-model="formData.params.surface_axis" placeholder="Select surface axis">
              <el-option label="X-axis (0)" :value="0" />
              <el-option label="Y-axis (1)" :value="1" />
              <el-option label="Z-axis (2)" :value="2" />
            </el-select>
          </el-form-item>
          
          <el-form-item>
            <el-checkbox v-model="formData.params.place_on_bottom">
              Place on bottom surface
            </el-checkbox>
          </el-form-item>
          
          <el-form-item>
            <template #label>
              <span>Adsorption Height (Å): </span>
              <el-tag size="small">{{ formData.params.adsorption_height }}</el-tag>
            </template>
            <el-slider
              v-model="formData.params.adsorption_height"
              :min="0.1"
              :max="10"
              :step="0.1"
              show-stops
            />
          </el-form-item>
          
          <el-form-item>
            <template #label>
              <span>Vacuum Thickness (Å): </span>
              <el-tag size="small">{{ formData.params.vacuum_thickness }}</el-tag>
            </template>
            <el-slider
              v-model="formData.params.vacuum_thickness"
              :min="5"
              :max="50"
              :step="1"
              show-stops
            />
          </el-form-item>
          
          <el-form-item>
            <template #label>
              <span>Collision Threshold (Å): </span>
              <el-tag size="small">{{ formData.params.collision_threshold }}</el-tag>
            </template>
            <el-slider
              v-model="formData.params.collision_threshold"
              :min="0.5"
              :max="3"
              :step="0.1"
              show-stops
            />
          </el-form-item>
        </el-collapse-item>
        
        <!-- Site Detection -->
        <el-collapse-item title="Site Detection" name="sites">
          <template #title>
            <el-icon><Location /></el-icon>
            <span style="margin-left: 8px;">Site Detection</span>
          </template>
          
          <el-form-item>
            <el-checkbox v-model="formData.params.hollow_sites_enabled">
              Enable hollow site detection
            </el-checkbox>
          </el-form-item>
          
          <el-form-item v-if="formData.params.hollow_sites_enabled" class="sub-params">
            <template #label>
              <span>KNN Neighbors: </span>
              <el-tag size="small">{{ formData.params.knn_neighbors }}</el-tag>
            </template>
            <el-slider
              v-model="formData.params.knn_neighbors"
              :min="1"
              :max="10"
              :step="1"
              show-stops
            />
          </el-form-item>
          
          <el-form-item>
            <el-checkbox v-model="formData.params.on_top_sites_enabled">
              Enable on-top site detection
            </el-checkbox>
          </el-form-item>
          
          <el-form-item v-if="formData.params.on_top_sites_enabled" label="Target Atom" class="sub-params">
            <el-input
              v-model="formData.params.on_top_target_atom"
              placeholder="e.g., O, C, N"
            >
              <template #prepend>
                <el-icon><Grid /></el-icon>
              </template>
            </el-input>
          </el-form-item>
        </el-collapse-item>
        
        <!-- Rotation Optimization -->
        <el-collapse-item title="Rotation Optimization" name="rotation">
          <template #title>
            <el-icon><Refresh /></el-icon>
            <span style="margin-left: 8px;">Rotation Optimization</span>
          </template>
          
          <el-form-item>
            <el-checkbox v-model="formData.params.rotation_method">
              Use spherical sampling method
            </el-checkbox>
          </el-form-item>
          
          <el-form-item v-if="formData.params.rotation_method" class="sub-params">
            <template #label>
              <span>Rotation Count: </span>
              <el-tag size="small">{{ formData.params.rotation_count }}</el-tag>
            </template>
            <el-slider
              v-model="formData.params.rotation_count"
              :min="10"
              :max="200"
              :step="10"
              show-stops
            />
          </el-form-item>
          
          <el-form-item v-if="formData.params.rotation_method" class="sub-params">
            <template #label>
              <span>Rotation Step (degrees): </span>
              <el-tag size="small">{{ formData.params.rotation_step }}</el-tag>
            </template>
            <el-slider
              v-model="formData.params.rotation_step"
              :min="1"
              :max="90"
              :step="1"
              show-stops
            />
          </el-form-item>
        </el-collapse-item>
      </el-collapse>
      
      <!-- Submit Button -->
      <el-form-item style="margin-top: 20px;">
        <el-button
          type="primary"
          native-type="submit"
          :loading="isRunning"
          :disabled="!canSubmit"
          size="large"
          style="width: 100%;"
        >
          <el-icon v-if="!isRunning"><VideoPlay /></el-icon>
          {{ isRunning ? 'Calculation Running...' : 'Start Calculation' }}
        </el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script>
import { Edit, Upload, UploadFilled, Setting, Location, Grid, Refresh, VideoPlay } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '../services/api'
import { DEFAULT_PARAMS } from '../utils/constants'

export default {
  name: 'CalculationForm',
  components: {
    Edit,
    Upload,
    UploadFilled,
    Setting,
    Location,
    Grid,
    Refresh,
    VideoPlay
  },
  props: {
    isRunning: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      activeCollapse: ['files'],
      formData: {
        files: {
          substrate: null,
          adsorbate: null
        },
        params: { ...DEFAULT_PARAMS }
      },
      substrateFileList: [],
      adsorbateFileList: [],
      errorMessage: ''
    }
  },
  computed: {
    canSubmit() {
      return this.formData.files.substrate && this.formData.files.adsorbate
    },
    filesUploaded() {
      return this.formData.files.substrate || this.formData.files.adsorbate
    },
    uploadedFilesCount() {
      let count = 0
      if (this.formData.files.substrate) count++
      if (this.formData.files.adsorbate) count++
      return count
    }
  },
  methods: {
    handleFileChange(type, uploadFile) {
      this.formData.files[type] = uploadFile.raw
      if (type === 'substrate') {
        this.substrateFileList = [uploadFile]
      } else {
        this.adsorbateFileList = [uploadFile]
      }
    },
    
    async submitCalculation() {
      this.errorMessage = ''
      
      if (!this.canSubmit) {
        ElMessage.warning('Please upload both substrate and adsorbate files')
        return
      }
      
      try {
        // Create FormData
        const formData = new FormData()
        formData.append('substrate_file', this.formData.files.substrate)
        formData.append('adsorbate_file', this.formData.files.adsorbate)
        
        // Add all parameters
        for (const [key, value] of Object.entries(this.formData.params)) {
          formData.append(key, value)
        }
        
        // Submit calculation
        const response = await api.submitCalculation(formData)
        
        if (response.success) {
          this.$emit('calculation-started', response)
          ElMessage.success('Calculation started successfully!')
        } else {
          this.errorMessage = response.message || 'Failed to start calculation'
          ElMessage.error(this.errorMessage)
        }
      } catch (error) {
        this.errorMessage = error.response?.data?.message || 'An error occurred'
        ElMessage.error(this.errorMessage)
        console.error('Calculation submission failed:', error)
      }
    }
  }
}
</script>

<style scoped>
.calculation-form-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
}

.sub-params {
  margin-left: 20px;
  padding-left: 15px;
  border-left: 2px solid var(--el-border-color-light);
}

:deep(.el-collapse-item__header) {
  font-weight: 500;
  padding-left: 10px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

.upload-demo {
  width: 100%;
}

:deep(.el-upload-dragger) {
  padding: 20px;
}
</style>
