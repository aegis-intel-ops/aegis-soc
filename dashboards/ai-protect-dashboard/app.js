const API_BASE = 'http://129.213.117.130:8010';

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

// Fawkes Upload
document.getElementById('fawkesForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById('imageFile');
    const results = document.getElementById('fawkesStatus');

    if (!fileInput.files[0]) {
        results.textContent = 'Please select an image file';
        return;
    }

    results.textContent = 'Uploading and processing...';

    const formData = new FormData();
    formData.append('image', fileInput.files[0]);

    try {
        const res = await fetch(`${API_BASE}/api/protect/fawkes`, {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        results.textContent = JSON.stringify(data, null, 2);
    } catch (e) {
        results.textContent = `Error: ${e.message}`;
    }
});

// Status Check
document.getElementById('statusForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const jobId = document.getElementById('jobId').value;
    const results = document.getElementById('jobResults');

    results.textContent = 'Checking status...';

    try {
        const res = await fetch(`${API_BASE}/api/protect/status/${jobId}`);
        const data = await res.json();
        results.textContent = JSON.stringify(data, null, 2);
    } catch (e) {
        results.textContent = `Error: ${e.message}`;
    }
});

// Init
checkHealth();
setInterval(checkHealth, 30000);
