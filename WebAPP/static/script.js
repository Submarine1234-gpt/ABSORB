document.addEventListener('DOMContentLoaded', function() {
    // --- Add new button elements ---
    const chartControls = document.getElementById('chart-controls');
    const scatterBtn = document.getElementById('scatter-btn');
    const heatmapBtn = document.getElementById('heatmap-btn');
    
    // --- Other variable declarations are the same ---
    const calculationForm = document.getElementById('calculation-form');
    const substrateFileInput = document.getElementById('substrate_file');
    const adsorbateFileInput = document.getElementById('adsorbate_file');
    const submitButton = document.getElementById('submit-button');
    const dashboard = document.getElementById('dashboard');
    const logOutput = document.getElementById('log-output');
    const heatmapContainer = document.getElementById('heatmap-container');
    const downloadLinkContainer = document.getElementById('result-download-link');
    const downloadButton = document.getElementById('download-button');
    const historyTableBody = document.querySelector('#results-table tbody');
    const step = parseFloat(document.getElementById('rotation_step').value);
    const count = parseInt(document.getElementById('rotation_count').value);

    const rotationMethodCheckbox = document.getElementById('rotation_method');
    const rotationCountInput = document.getElementById('rotation_count');
    const rotationStepInput = document.getElementById('rotation_step');
    const rotationMethodOptions = document.getElementById('rotation-method-options');
    const hollowSitesCheckbox = document.getElementById('hollow_sites_enabled');
    const knnNeighborsInput = document.getElementById('knn_neighbors');
    const hollowDedupInput = document.getElementById('hollow_site_deduplication_distance');
    const hollowOptions = document.getElementById('hollow-options');
    const onTopSitesCheckbox = document.getElementById('on_top_sites_enabled');
    const onTopTargetInput = document.getElementById('on_top_target_atom');
    const onTopOptions = document.getElementById('on-top-options-container');
    function updateRotationMethodParams() {
        const enabled = rotationMethodCheckbox.checked;
        rotationCountInput.disabled = !enabled;
        rotationStepInput.disabled = !enabled;
        rotationMethodOptions.style.opacity = enabled ? '' : '0.6';
    }
    function updateHollowParams() {
        const enabled = hollowSitesCheckbox.checked;
        knnNeighborsInput.disabled = !enabled;
        hollowDedupInput.disabled = !enabled;
        hollowOptions.style.opacity = enabled ? '' : '0.6';
    } 
    function updateOnTopParams() {
        const enabled = onTopSitesCheckbox.checked;
        onTopTargetInput.disabled = !enabled;
        onTopOptions.style.opacity = enabled ? '' : '0.6';
    }
    updateRotationMethodParams();
    updateHollowParams();
    updateOnTopParams();
    rotationMethodCheckbox.addEventListener('change', updateRotationMethodParams);
    hollowSitesCheckbox.addEventListener('change', updateHollowParams);
    onTopSitesCheckbox.addEventListener('change', updateOnTopParams);





    let activeEventSource = null;
    let activeSessionId = null;
    let activeSurfaceAxis = '2';
    let heatmapChart = null;
    
    // --- NEW: Store loaded data and current chart type ---
    let loadedVizData = null;
    let currentChartType = 'scatter';

    // --- Event Listeners ---
    calculationForm.addEventListener('submit', handleFormSubmit);
    historyTableBody.addEventListener('click', handleHistoryViewClick);
    scatterBtn.addEventListener('click', () => switchChartView('scatter'));
    heatmapBtn.addEventListener('click', () => switchChartView('heatmap'));

    refreshHistory();

    // --- NEW: Function to switch chart view ---
    function switchChartView(type) {
        currentChartType = type;
        scatterBtn.classList.toggle('active', type === 'scatter');
        heatmapBtn.classList.toggle('active', type === 'heatmap');
        // Re-render the chart with the currently loaded data
        if (loadedVizData) {
            if (type === 'scatter') {
                renderScatterChart(loadedVizData.surface, loadedVizData.adsorption, loadedVizData.axis);
            } else {
                renderHeatmapChart(loadedVizData.adsorption, loadedVizData.axis);
            }
        }
    }

    function handleFormSubmit(event) {
        event.preventDefault();
        if (substrateFileInput.files.length === 0 || adsorbateFileInput.files.length === 0) {
            alert('Please upload both a substrate and an adsorbate file.'); return;
        }
        if (activeEventSource) activeEventSource.close();
        resetDashboard();
        const formData = new FormData(calculationForm);
        submitButton.disabled = true;
        submitButton.textContent = '计算中...';
        dashboard.classList.remove('hidden');

        fetch('/run-calculation', { method: 'POST', body: formData })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                activeSessionId = data.session_id;
                activeSurfaceAxis = data.surface_axis || '2';
                logOutput.innerHTML = `<div>[SYSTEM] Calculation started. Session ID: ${activeSessionId}</div>`;
                startLogStream(data.session_id);
            } else { throw new Error(data.message); }
        })
        .catch(error => {
            logOutput.innerHTML += `<div class="log-error">[ERROR] Submission failed: ${error.message}</div>`;
            resetUiAfterCalculation();
        });
    }

    function startLogStream(sessionId) {
        if (activeEventSource) activeEventSource.close();
        activeEventSource = new EventSource(`/stream-logs/${sessionId}`);
        activeEventSource.onmessage = function(event) {
            const line = event.data;
            logOutput.innerHTML += `<div>${line}</div>`;
            logOutput.scrollTop = logOutput.scrollHeight;
            if (line.includes('Log stream finished')) {
                activeEventSource.close();
                pollForCompletion(sessionId);
            }
        };
        activeEventSource.onerror = function() {
            logOutput.innerHTML += '<div class="log-error">[SYSTEM] Log stream disconnected. Checking status...</div>';
            activeEventSource.close();
            if (sessionId) pollForCompletion(sessionId);
            else resetUiAfterCalculation();
        };
    }

    function handleHistoryViewClick(event) {
        if (event.target.tagName !== 'BUTTON' || !event.target.dataset.session) return;
        if (submitButton.disabled) {
            alert("Please wait for the current calculation to finish before viewing past results."); return;
        }
        const sessionId = event.target.dataset.session;
        const surfaceAxis = event.target.dataset.axis || '2';
        resetDashboard();
        dashboard.classList.remove('hidden');
        logOutput.innerHTML = `<div>[SYSTEM] Displaying results for past session: ${sessionId}</div>`;
        loadVisualization(sessionId, surfaceAxis);
    }
    
    function pollForCompletion(sessionId) {
        logOutput.innerHTML += '<div>[SYSTEM] Finalizing results...</div>';
        logOutput.scrollTop = logOutput.scrollHeight;
        let attempts = 0;
        const interval = setInterval(() => {
            fetch(`/check-status/${sessionId}`)
                .then(res => res.json())
                .then(data => {
                    attempts++;
                    if (data.status === 'complete' || attempts >= 10) {
                        clearInterval(interval);
                        loadVisualization(sessionId, activeSurfaceAxis);
                        resetUiAfterCalculation();
                    }
                })
                .catch(() => { clearInterval(interval); resetUiAfterCalculation(); });
        }, 500);
    }

    function resetUiAfterCalculation() {
        submitButton.disabled = false;
        submitButton.textContent = '开始计算';
        refreshHistory();
    }
    
    function loadVisualization(sessionId, surfaceAxis) {
        downloadButton.href = `/download-result/${sessionId}`;
        downloadLinkContainer.classList.remove('hidden');
        const surfaceDataPromise = fetch(`/get-viz-data/${sessionId}/surface_atoms.json`).then(res => res.json());
        const adsorptionDataPromise = fetch(`/get-viz-data/${sessionId}/adsorption_sites.json`).then(res => res.json());
        
        Promise.all([surfaceDataPromise, adsorptionDataPromise])
            .then(([surfaceData, adsorptionData]) => {
                if (surfaceData.error || adsorptionData.error) throw new Error(surfaceData.error || adsorptionData.error);
                
                // --- MODIFIED: Store data and show controls ---
                loadedVizData = { surface: surfaceData, adsorption: adsorptionData, axis: surfaceAxis };
                chartControls.classList.remove('hidden');
                heatmapContainer.classList.remove('hidden');
                switchChartView(currentChartType); // Render the currently selected chart type
            })
            .catch(error => {
                heatmapContainer.classList.remove('hidden');
                heatmapContainer.innerHTML = `<p>Failed to load visualization data: ${error.message}</p>`;
            });
    }

    // --- RENAMED from renderCombinedChart ---
    function renderScatterChart(surfaceData, adsorptionData, surfaceAxis) {
        if (heatmapChart) heatmapChart.dispose();
        heatmapChart = echarts.init(heatmapContainer);
        let plotAxes; const axisNames = ['X', 'Y', 'Z']; const normalAxis = parseInt(surfaceAxis, 10);
        if (normalAxis === 0) { plotAxes = { x: 1, y: 2 }; } else if (normalAxis === 1) { plotAxes = { x: 0, y: 2 }; } else { plotAxes = { x: 0, y: 1 }; }
        const energyValues = adsorptionData.sites.map(site => site.energy);
        heatmapChart.setOption({
            title: { text: 'Surface Atoms and Adsorption Sites (Scatter)', left: 'center' },
            legend: { top: 30, data: ['Surface Atoms', 'Adsorption Sites'] },
            tooltip: { formatter: params => `<b>${params.seriesName}</b><br/>${axisNames[plotAxes.x]}: ${params.value[0].toFixed(2)}<br/>${axisNames[plotAxes.y]}: ${params.value[1].toFixed(2)}<br/>` + (params.seriesName === 'Adsorption Sites' ? `Energy: ${params.value[2].toFixed(4)} eV` : '') },
            grid: { top: 70, right: 150, bottom: 60, left: 70 },
            xAxis: { type: 'value', name: axisNames[plotAxes.x], scale: true },
            yAxis: { type: 'value', name: axisNames[plotAxes.y], scale: true },
            visualMap: { seriesIndex: 1, min: Math.min(...energyValues), max: Math.max(...energyValues), calculable: true, orient: 'vertical', right: 10, top: 'center', text: ['High', 'Low'], inRange: { color: ['#a50026', '#d73027', '#f46d43', '#fdae61', '#fee090', '#ffffbf', '#e0f3f8', '#abd9e9', '#74add1', '#4575b4', '#313695'].reverse() } },
            series: [
                { name: 'Surface Atoms', type: 'scatter', symbolSize: 8, data: surfaceData.coords.map(c => [c[plotAxes.x], c[plotAxes.y]]), itemStyle: { color: '#999', opacity: 0.7 } },
                { name: 'Adsorption Sites', type: 'scatter', symbolSize: 15, data: adsorptionData.sites.map(s => [s.coords[plotAxes.x], s.coords[plotAxes.y], s.energy]), itemStyle: { borderColor: '#555', borderWidth: 1 } }
            ]
        });
    }

    // --- NEW: Function to render the heatmap view ---
    function renderHeatmapChart(adsorptionData, surfaceAxis) {
        if (heatmapChart) heatmapChart.dispose();
        heatmapChart = echarts.init(heatmapContainer);
        let plotAxes; const axisNames = ['X', 'Y', 'Z']; const normalAxis = parseInt(surfaceAxis, 10);
        if (normalAxis === 0) { plotAxes = { x: 1, y: 2 }; } else if (normalAxis === 1) { plotAxes = { x: 0, y: 2 }; } else { plotAxes = { x: 0, y: 1 }; }
        const energyValues = adsorptionData.sites.map(site => site.energy);
        heatmapChart.setOption({
            title: { text: 'Adsorption Energy (Heatmap)', left: 'center' },
            tooltip: { formatter: params => `<b>Adsorption Site</b><br/>${axisNames[plotAxes.x]}: ${params.value[0].toFixed(2)}<br/>${axisNames[plotAxes.y]}: ${params.value[1].toFixed(2)}<br/>Energy: ${params.value[2].toFixed(4)} eV` },
            grid: { top: 70, right: 150, bottom: 60, left: 70 },
            xAxis: { type: 'value', name: axisNames[plotAxes.x], scale: true },
            yAxis: { type: 'value', name: axisNames[plotAxes.y], scale: true },
            visualMap: { min: Math.min(...energyValues), max: Math.max(...energyValues), calculable: true, orient: 'vertical', right: 10, top: 'center', text: ['High', 'Low'], inRange: { color: ['#a50026', '#d73027', '#f46d43', '#fdae61', '#fee090', '#ffffbf', '#e0f3f8', '#abd9e9', '#74add1', '#4575b4', '#313695'].reverse() } },
            series: [{
                name: 'Adsorption Sites',
                type: 'scatter',
                symbol: 'rect', // Use squares instead of circles
                symbolSize: 20, // Make them larger to look like a heatmap
                data: adsorptionData.sites.map(s => [s.coords[plotAxes.x], s.coords[plotAxes.y], s.energy]),
                itemStyle: { opacity: 0.7 } // Add opacity to see overlaps
            }]
        });
    }
    
    function resetDashboard() {
        dashboard.classList.add('hidden');
        chartControls.classList.add('hidden'); // Hide chart controls
        heatmapContainer.classList.add('hidden');
        downloadLinkContainer.classList.add('hidden');
        if (heatmapChart) { heatmapChart.dispose(); heatmapChart = null; }
        if (activeEventSource) { activeEventSource.close(); activeEventSource = null; }
        activeSessionId = null;
        loadedVizData = null; // Clear loaded data
    }

    function refreshHistory() {
        fetch('/get-results')
            .then(res => res.json())
            .then(data => {
                historyTableBody.innerHTML = '';
                data.forEach(result => {
                    const row = historyTableBody.insertRow();
                    row.innerHTML = `
                        <td>${result.timestamp}</td>
                        <td>${result.filename}</td>
                        <td>
                            <a href="/download-result/${result.session_id}" class="button-small" download>Download</a>
                            <button class="button-small" data-session="${result.session_id}" data-axis="${result.surface_axis || '2'}">View</button>
                        </td>`;
                });
            });
    }
});