<template>
  <el-card shadow="hover" class="result-history-card">
    <template #header>
      <div class="card-header">
        <span>
          <el-icon><Clock /></el-icon>
          Calculation History
        </span>
        <el-tag v-if="results.length > 0" type="info">{{ results.length }} results</el-tag>
      </div>
    </template>
    
    <el-empty v-if="results.length === 0" description="No calculations yet. Start your first calculation above!" />
    
    <div v-else>
      <el-table
        :data="paginatedResults"
        stripe
        style="width: 100%"
        :default-sort="{ prop: 'timestamp', order: 'descending' }"
      >
        <el-table-column prop="timestamp" label="Date/Time" width="180" sortable />
        <el-table-column prop="session_id" label="Session ID" width="150">
          <template #default="scope">
            <el-tooltip :content="scope.row.session_id" placement="top">
              <code>{{ scope.row.session_id.substring(0, 8) }}...</code>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="surface_axis" label="Surface Axis" width="120">
          <template #default="scope">
            <el-tag size="small" type="success">{{ getSurfaceAxisLabel(scope.row.surface_axis) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="220" fixed="right">
          <template #default="scope">
            <el-button-group>
              <el-button
                size="small"
                type="primary"
                @click="loadResult(scope.row)"
                :icon="View"
              >
                View
              </el-button>
              <el-button
                size="small"
                type="success"
                @click="downloadResult(scope.row.session_id)"
                :icon="Download"
              >
                Download
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-if="results.length > pageSize"
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="results.length"
        layout="prev, pager, next, total"
        class="pagination"
      />
    </div>
  </el-card>
</template>

<script>
import { Clock, View, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '../services/api'

export default {
  name: 'ResultHistory',
  components: {
    Clock,
    View,
    Download
  },
  props: {
    results: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      currentPage: 1,
      pageSize: 10
    }
  },
  computed: {
    paginatedResults() {
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      return this.results.slice(start, end)
    }
  },
  methods: {
    getSurfaceAxisLabel(axis) {
      const labels = ['X (0)', 'Y (1)', 'Z (2)']
      return labels[axis] || axis
    },
    
    loadResult(result) {
      this.$emit('load-result', result)
    },
    
    downloadResult(sessionId) {
      window.location.href = api.getDownloadUrl(sessionId)
      ElMessage.success('Download started')
    }
  }
}
</script>

<style scoped>
.result-history-card {
  margin-top: 20px;
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

code {
  font-family: 'Courier New', 'Consolas', monospace;
  background: #f4f4f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.875rem;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

:deep(.el-table__row) {
  cursor: pointer;
}
</style>
