const API_BASE = 'http://129.213.117.130:8020';

// Health check
async function checkHealth() {
    const status = document.getElementById('status');
    try {
        const res = await fetch(`${API_BASE}/health`);
        if (res.ok) {
            status.textContent = '● Connected';
            status.classList.remove('error');
        } else {
            throw new Error('API not responding');
        }
    } catch (e) {
        status.textContent = '○ Disconnected';
        status.classList.add('error');
    }
}

// Analyze Audio
document.getElementById('analyzeForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById('audioFile');
    const results = document.getElementById('analyzeResults');

    if (!fileInput.files[0]) {
        results.textContent = 'Please select an audio file';
        return;
    }

    results.textContent = 'Analyzing audio...';

    const formData = new FormData();
    formData.append('audio', fileInput.files[0]);

    try {
        const res = await fetch(`${API_BASE}/api/voice/analyze`, {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        results.textContent = JSON.stringify(data, null, 2);
    } catch (e) {
        results.textContent = `Error: ${e.message}`;
    }
});

// Add Watermark
document.getElementById('watermarkForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById('watermarkFile');
    const owner = document.getElementById('owner').value;
    const results = document.getElementById('watermarkResults');

    if (!fileInput.files[0]) {
        results.textContent = 'Please select an audio file';
        return;
    }

    results.textContent = 'Adding watermark...';

    const formData = new FormData();
    formData.append('audio', fileInput.files[0]);
    if (owner) formData.append('owner', owner);

    try {
        const res = await fetch(`${API_BASE}/api/voice/watermark`, {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        results.textContent = JSON.stringify(data, null, 2);
    } catch (e) {
        results.textContent = `Error: ${e.message}`;
    }
});

// Verify Watermark
document.getElementById('verifyForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const watermarkId = document.getElementById('watermarkId').value;
    const results = document.getElementById('verifyResults');

    results.textContent = 'Verifying...';

    try {
        const res = await fetch(`${API_BASE}/api/voice/verify/${watermarkId}`);
        const data = await res.json();
        results.textContent = JSON.stringify(data, null, 2);
    } catch (e) {
        results.textContent = `Error: ${e.message}`;
    }
});

// Init
checkHealth();
setInterval(checkHealth, 30000);
