# ABSORB Platform - Quick Reference Guide

## 🚀 Quick Start

### Installation (First Time)
```bash
# Install dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..
```

### Running the Application
```bash
# Linux/Mac
./start.sh

# Windows
start.bat

# Manual (Backend)
cd backend && python app.py

# Manual (Frontend)
cd frontend && npm run dev
```

### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health

## 📁 Project Structure

```
ABSORB/
│
├── 📂 backend/                    # Flask Backend Application
│   ├── 📄 app.py                  # Main Flask app (REST API)
│   ├── 📄 config.py               # Configuration (no hardcoding!)
│   │
│   ├── 📂 core/                   # Core Calculation Engine
│   │   ├── 📄 workflow.py         # Main orchestrator
│   │   ├── 📂 calculators/        # Calculator factory
│   │   │   └── calculator_factory.py
│   │   ├── 📂 site_finder/        # Site detection
│   │   │   ├── base_finder.py
│   │   │   ├── hollow_finder.py   # KNN-based hollow sites
│   │   │   └── ontop_finder.py    # Atom-based on-top sites
│   │   └── 📂 optimizers/         # Geometry optimization
│   │       ├── base_optimizer.py
│   │       └── rotation_optimizer.py  # Normal & spherical
│   │
│   ├── 📂 services/               # Service Layer
│   │   ├── calculation_service.py # Background calculations
│   │   ├── file_service.py        # File handling & ZIP
│   │   └── session_service.py     # Session management
│   │
│   └── 📂 utils/                  # Utilities
│       ├── logger.py              # Logging system
│       └── validators.py          # Input validation
│
├── 📂 frontend/                   # Vue.js Frontend
│   ├── 📄 package.json            # Dependencies
│   ├── 📄 vite.config.js          # Build config
│   │
│   └── 📂 src/
│       ├── 📄 main.js             # Entry point
│       ├── 📄 App.vue             # Root component
│       │
│       ├── 📂 components/         # Vue Components
│       │   ├── Dashboard.vue      # Main dashboard
│       │   ├── CalculationForm.vue
│       │   ├── ChartControls.vue
│       │   ├── VisualizationChart.vue
│       │   └── ResultHistory.vue
│       │
│       ├── 📂 services/
│       │   └── api.js             # API client
│       │
│       └── 📂 utils/
│           └── constants.js       # Constants
│
├── 📄 requirements.txt            # Python dependencies
├── 📄 README.md                   # Full documentation
├── 📄 IMPLEMENTATION_SUMMARY.md   # Architecture details
├── 📄 validate_structure.py       # Structure validator
├── 🔧 start.sh                    # Linux/Mac startup
└── 🔧 start.bat                   # Windows startup
```

## 🔄 Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface (Vue.js)                   │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ Calculation │  │ Real-time    │  │ 3D Visualization │   │
│  │ Form        │  │ Logs (SSE)   │  │ (Plotly.js)      │   │
│  └──────┬──────┘  └──────┬───────┘  └────────┬─────────┘   │
└─────────┼─────────────────┼───────────────────┼─────────────┘
          │                 │                   │
          │ HTTP POST       │ EventSource       │ HTTP GET
          ▼                 ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    Flask REST API                            │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐   │
│  │ File Upload  │  │ Log Stream  │  │ Viz Data         │   │
│  │ & Validation │  │ (SSE)       │  │ Provider         │   │
│  └──────┬───────┘  └──────┬──────┘  └────────┬─────────┘   │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                             │
│  ┌──────────────────┐  ┌────────────┐  ┌─────────────────┐ │
│  │ CalculationService│  │FileService │  │ SessionService  │ │
│  │ (Threading)       │  │(ZIP/Upload)│  │ (History)       │ │
│  └─────────┬─────────┘  └─────┬──────┘  └────────┬────────┘ │
└────────────┼────────────────────┼──────────────────┼──────────┘
             │                    │                  │
             ▼                    ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                  Core Calculation Engine                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │            SurfaceAdsorptionWorkflow                  │  │
│  │                                                       │  │
│  │  1. Load Structures (ASE)                            │  │
│  │  2. Build Surface Slab                               │  │
│  │  3. Find Surface Atoms                               │  │
│  │  4. Detect Sites ──► HollowFinder + OnTopFinder      │  │
│  │  5. For each site:                                   │  │
│  │     ├─ Place Adsorbate                               │  │
│  │     ├─ Optimize Rotation ──► RotationOptimizer       │  │
│  │     ├─ Calculate Energy ──► CHGNet Calculator        │  │
│  │     └─ Check Collisions                              │  │
│  │  6. Generate Results                                 │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Key Features

### Backend Features
- ✅ **Factory Pattern**: Extensible calculators and optimizers
- ✅ **Service Layer**: Calculation, file, and session services
- ✅ **Thread Safety**: Lock-based result management
- ✅ **Validation**: Comprehensive input validation
- ✅ **Logging**: Multi-level logging system
- ✅ **Real-time**: Server-Sent Events for log streaming

### Frontend Features
- ✅ **Reactive UI**: Vue.js 3 with composition API support
- ✅ **Real-time Logs**: Live calculation monitoring
- ✅ **3D Visualization**: Interactive Plotly charts
- ✅ **Form Validation**: Client-side parameter validation
- ✅ **Result History**: Browse and download past calculations
- ✅ **Responsive**: Mobile-friendly design

### Calculation Features
- ✅ **Hollow Sites**: KNN-based cluster analysis
- ✅ **On-top Sites**: Specific atom targeting
- ✅ **Rotation**: Normal axis or spherical sampling
- ✅ **Energy**: CHGNet ML potential (fast & accurate)
- ✅ **Collision**: Automatic collision detection
- ✅ **Visualization**: JSON output for 3D plotting

## 🔧 Configuration

### Backend Config (`backend/config.py`)
```python
DEFAULT_PARAMS = {
    'surface_axis': 2,           # 0=X, 1=Y, 2=Z
    'adsorption_height': 2.0,    # Å
    'vacuum_thickness': 20.0,    # Å
    'collision_threshold': 1.2,  # Å
    'hollow_sites_enabled': True,
    'on_top_sites_enabled': True,
    'rotation_count': 50,        # Spherical samples
    'rotation_step': 30,         # Degrees
    # ... more parameters
}
```

### Frontend Proxy (`frontend/vite.config.js`)
```javascript
server: {
  port: 3000,
  proxy: {
    '/run-calculation': 'http://localhost:5000',
    '/check-status': 'http://localhost:5000',
    // ... more endpoints
  }
}
```

## 📊 API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/run-calculation` | POST | Submit calculation |
| `/check-status/<id>` | GET | Check status |
| `/stream-logs/<id>` | GET | Stream logs (SSE) |
| `/get-viz-data/<id>/<file>` | GET | Get visualization data |
| `/get-results` | GET | Get all results |
| `/download-result/<id>` | GET | Download ZIP |
| `/api/health` | GET | Health check |

## 📦 Dependencies

### Backend (Python)
```
Flask==2.3.3
ase==3.22.1
chgnet==0.3.0
numpy==1.24.3
scipy==1.11.2
torch==2.0.1
```

### Frontend (Node.js)
```json
{
  "vue": "^3.3.4",
  "axios": "^1.5.0",
  "plotly.js-dist-min": "^2.26.0",
  "@vitejs/plugin-vue": "^4.3.4",
  "vite": "^4.4.9"
}
```

## 🧪 Testing

### Validate Structure
```bash
python validate_structure.py
```

### Test Backend
```bash
cd backend
python app.py
# Visit http://localhost:5000/api/health
```

### Test Frontend
```bash
cd frontend
npm run dev
# Visit http://localhost:3000
```

## 📝 Usage Example

1. **Start Application**: `./start.sh`
2. **Open Browser**: http://localhost:3000
3. **Upload Files**: Select substrate and adsorbate CIF files
4. **Configure**: Adjust parameters as needed
5. **Submit**: Click "Start Calculation"
6. **Monitor**: Watch real-time logs
7. **Visualize**: View 3D results when complete
8. **Download**: Get complete result package

## 🎨 Design Principles

- **Modularity**: Each module has single responsibility
- **Extensibility**: Easy to add new calculators/finders
- **Maintainability**: Clear structure and documentation
- **Configurability**: No hardcoded values
- **Reliability**: Comprehensive error handling
- **Performance**: Threading and efficient algorithms

## 📚 Documentation

- `README.md` - Full documentation
- `IMPLEMENTATION_SUMMARY.md` - Architecture details
- `backend/` - Python docstrings in all modules
- `frontend/src/` - JSDoc comments in services

## 🔐 Security

- ✅ File type validation (CIF only)
- ✅ File size limits (16MB)
- ✅ Filename sanitization
- ✅ Parameter range validation
- ✅ Session isolation
- ✅ No user code execution

## 🚀 Production Deployment

1. Build frontend: `cd frontend && npm run build`
2. Configure WSGI server (gunicorn/uWSGI)
3. Set up reverse proxy (nginx)
4. Configure environment variables
5. Set up process management
6. Enable HTTPS

## ✅ Validation Checklist

- [x] All 40 files created
- [x] Structure validation passed
- [x] Python syntax verified
- [x] JSON configurations valid
- [x] Documentation complete
- [x] Start scripts executable

---

**For detailed architecture and implementation notes, see `IMPLEMENTATION_SUMMARY.md`**

**For full documentation and troubleshooting, see `README.md`**
