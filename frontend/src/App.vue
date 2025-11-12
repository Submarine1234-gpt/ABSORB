<template>
  <el-container class="app-container">
    <el-header class="app-header" height="120px">
      <div class="header-content">
        <h1 class="header-title">
          <el-icon><Grid /></el-icon>
          ABSORB
        </h1>
        <p class="header-subtitle">Surface Adsorption Calculation Platform</p>
        <div class="header-actions">
          <el-tooltip content="Toggle Dark Mode" placement="bottom">
            <el-switch
              v-model="isDark"
              @change="toggleDarkMode"
              inline-prompt
              :active-icon="Moon"
              :inactive-icon="Sunny"
            />
          </el-tooltip>
        </div>
      </div>
    </el-header>
    
    <el-main class="app-main">
      <Dashboard 
        @start-calculation="handleStartCalculation"
        :current-session="currentSession"
      />
    </el-main>
    
    <el-footer class="app-footer" height="60px">
      <div class="footer-content">
        <el-icon><Copyright /></el-icon>
        <span>2024 ABSORB Platform | Powered by ASE & CHGNet</span>
      </div>
    </el-footer>
  </el-container>
</template>

<script>
import { Moon, Sunny, Grid, Copyright } from '@element-plus/icons-vue'
import Dashboard from './components/Dashboard.vue'

export default {
  name: 'App',
  components: {
    Dashboard,
    Moon,
    Sunny,
    Grid,
    Copyright
  },
  data() {
    return {
      currentSession: null,
      isDark: false
    }
  },
  methods: {
    handleStartCalculation(sessionData) {
      this.currentSession = sessionData
    },
    toggleDarkMode() {
      if (this.isDark) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    }
  },
  mounted() {
    // Initialize dark mode from localStorage
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme === 'dark') {
      this.isDark = true
      document.documentElement.classList.add('dark')
    }
  },
  watch: {
    isDark(newVal) {
      localStorage.setItem('theme', newVal ? 'dark' : 'light')
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: #f5f7fa;
  min-height: 100vh;
}

#app {
  min-height: 100vh;
}

.app-container {
  min-height: 100vh;
  background: #f5f7fa;
}

.app-header {
  background: linear-gradient(135deg, #409EFF 0%, #53a8ff 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  position: relative;
}

.header-content {
  text-align: center;
  width: 100%;
}

.header-title {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}

.header-subtitle {
  font-size: 1.1rem;
  opacity: 0.95;
}

.header-actions {
  position: absolute;
  right: 2rem;
  top: 50%;
  transform: translateY(-50%);
}

.app-main {
  padding: 2rem;
  max-width: 1600px;
  width: 100%;
  margin: 0 auto;
}

.app-footer {
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  border-top: 1px solid #e4e7ed;
  color: #909399;
}

.footer-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Dark mode support */
.dark {
  background: #1a1a1a;
  color: #e4e7ed;
}

.dark .app-container {
  background: #1a1a1a;
}

.dark .app-footer {
  background: #2c2c2c;
  border-top-color: #4c4d4f;
}

/* Responsive design */
@media (max-width: 768px) {
  .app-main {
    padding: 1rem;
  }
  
  .header-title {
    font-size: 1.8rem;
  }
  
  .header-subtitle {
    font-size: 0.9rem;
  }
  
  .header-actions {
    right: 1rem;
  }
}
</style>
