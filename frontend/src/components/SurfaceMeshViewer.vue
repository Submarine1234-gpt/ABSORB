<template>
  <div class="mesh-viewer-container" ref="container">
    <div v-if="loading" class="mesh-loading">
      <el-skeleton :rows="6" animated />
    </div>
    <div v-else-if="error">
      <el-empty description="Failed to load mesh data">
        <el-button type="primary" @click="loadMeshData">Retry</el-button>
      </el-empty>
    </div>
    <div v-else-if="!meshData">
      <el-empty description="No mesh data available" />
    </div>
    <canvas v-show="meshData && !loading && !error" ref="canvas"></canvas>
  </div>
</template>

<script>
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'
import api from '../services/api'

export default {
  name: 'SurfaceMeshViewer',
  props: {
    sessionId: {
      type: String,
      required: true
    },
    meshOptions: {
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
      loading: false,
      error: null,
      meshData: null,
      scene: null,
      camera: null,
      renderer: null,
      controls: null,
      mesh: null,
      animationId: null
    }
  },
  watch: {
    sessionId: {
      immediate: true,
      handler() {
        this.loadMeshData()
      }
    },
    meshOptions: {
      deep: true,
      handler() {
        this.updateMeshDisplay()
      }
    }
  },
  mounted() {
    this.initThreeJS()
    window.addEventListener('resize', this.onWindowResize)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.onWindowResize)
    if (this.animationId) {
      cancelAnimationFrame(this.animationId)
    }
    if (this.renderer) {
      this.renderer.dispose()
    }
  },
  methods: {
    initThreeJS() {
      if (!this.$refs.canvas) return
      
      // Scene
      this.scene = new THREE.Scene()
      this.scene.background = new THREE.Color(0xf5f7fa)
      
      // Camera
      this.camera = new THREE.PerspectiveCamera(
        75,
        this.$refs.container.clientWidth / this.$refs.container.clientHeight,
        0.1,
        1000
      )
      this.camera.position.set(5, 5, 5)
      
      // Renderer
      this.renderer = new THREE.WebGLRenderer({
        canvas: this.$refs.canvas,
        antialias: true
      })
      this.renderer.setSize(
        this.$refs.container.clientWidth,
        this.$refs.container.clientHeight
      )
      
      // Controls
      this.controls = new OrbitControls(this.camera, this.renderer.domElement)
      this.controls.enableDamping = true
      this.controls.dampingFactor = 0.05
      
      // Lights
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.6)
      this.scene.add(ambientLight)
      
      const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
      directionalLight.position.set(10, 10, 10)
      this.scene.add(directionalLight)
      
      // Grid helper
      const gridHelper = new THREE.GridHelper(10, 10)
      this.scene.add(gridHelper)
      
      // Axes helper
      const axesHelper = new THREE.AxesHelper(5)
      this.scene.add(axesHelper)
      
      this.animate()
    },
    
    async loadMeshData() {
      this.loading = true
      this.error = null
      
      try {
        // Try to load mesh data from API
        const meshData = await api.getMeshData(this.sessionId)
        this.meshData = meshData
        this.createMesh()
      } catch (err) {
        // If mesh endpoint doesn't exist yet, show placeholder
        console.warn('Mesh data not available yet:', err)
        this.error = 'Mesh data not yet generated'
      } finally {
        this.loading = false
      }
    },
    
    createMesh() {
      if (!this.meshData || !this.scene) return
      
      // Remove old mesh if exists
      if (this.mesh) {
        this.scene.remove(this.mesh)
        this.mesh.geometry.dispose()
        this.mesh.material.dispose()
      }
      
      const { vertices, triangles, energies } = this.meshData
      
      // Create BufferGeometry
      const geometry = new THREE.BufferGeometry()
      
      // Flatten vertices array
      const positions = new Float32Array(vertices.flat())
      geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
      
      // Create color attribute based on energies
      const colors = this.generateColors(energies)
      geometry.setAttribute('color', new THREE.BufferAttribute(new Float32Array(colors), 3))
      
      // Set indices for triangles
      const indices = new Uint32Array(triangles.flat())
      geometry.setIndex(new THREE.BufferAttribute(indices, 1))
      
      // Compute normals for lighting
      geometry.computeVertexNormals()
      
      // Create material
      const material = new THREE.MeshPhongMaterial({
        vertexColors: true,
        side: THREE.DoubleSide,
        wireframe: this.meshOptions.wireframe,
        opacity: this.meshOptions.opacity,
        transparent: this.meshOptions.opacity < 1.0
      })
      
      // Create mesh
      this.mesh = new THREE.Mesh(geometry, material)
      this.scene.add(this.mesh)
      
      // Center and scale the mesh
      this.centerMesh()
    },
    
    generateColors(energies) {
      if (!energies || energies.length === 0) {
        return new Array(vertices.length * 3).fill(0.5)
      }
      
      const minE = Math.min(...energies)
      const maxE = Math.max(...energies)
      const range = maxE - minE || 1
      
      const colors = []
      for (const energy of energies) {
        const normalized = (energy - minE) / range
        const color = this.getColorForValue(normalized)
        colors.push(color.r, color.g, color.b)
      }
      
      return colors
    },
    
    getColorForValue(value) {
      // Color mapping: green (good) -> yellow (medium) -> red (bad)
      // value: 0 (low energy, favorable) to 1 (high energy, unfavorable)
      
      if (value < 0.5) {
        // Green to Yellow
        const t = value * 2
        return {
          r: t,
          g: 1,
          b: 0
        }
      } else {
        // Yellow to Red
        const t = (value - 0.5) * 2
        return {
          r: 1,
          g: 1 - t,
          b: 0
        }
      }
    },
    
    centerMesh() {
      if (!this.mesh) return
      
      // Compute bounding box
      const box = new THREE.Box3().setFromObject(this.mesh)
      const center = box.getCenter(new THREE.Vector3())
      const size = box.getSize(new THREE.Vector3())
      
      // Center the mesh
      this.mesh.position.sub(center)
      
      // Adjust camera to fit the mesh
      const maxDim = Math.max(size.x, size.y, size.z)
      const fov = this.camera.fov * (Math.PI / 180)
      let cameraZ = Math.abs(maxDim / Math.sin(fov / 2)) * 1.5
      this.camera.position.set(cameraZ, cameraZ, cameraZ)
      this.camera.lookAt(0, 0, 0)
      this.controls.update()
    },
    
    updateMeshDisplay() {
      if (!this.mesh) return
      
      this.mesh.material.wireframe = this.meshOptions.wireframe
      this.mesh.material.opacity = this.meshOptions.opacity
      this.mesh.material.transparent = this.meshOptions.opacity < 1.0
      this.mesh.material.needsUpdate = true
    },
    
    animate() {
      this.animationId = requestAnimationFrame(this.animate)
      this.controls.update()
      this.renderer.render(this.scene, this.camera)
    },
    
    onWindowResize() {
      if (!this.$refs.container || !this.camera || !this.renderer) return
      
      const width = this.$refs.container.clientWidth
      const height = this.$refs.container.clientHeight
      
      this.camera.aspect = width / height
      this.camera.updateProjectionMatrix()
      this.renderer.setSize(width, height)
    }
  }
}
</script>

<style scoped>
.mesh-viewer-container {
  width: 100%;
  height: 600px;
  position: relative;
  background: #f5f7fa;
  border-radius: 4px;
  overflow: hidden;
}

.mesh-loading {
  padding: 20px;
}

canvas {
  display: block;
  width: 100%;
  height: 100%;
}
</style>
