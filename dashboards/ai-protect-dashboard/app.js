const API_BASE = '';

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

// Protection Form
document.getElementById('method').addEventListener('change', (e) => {
    const info = document.getElementById('queueInfo');
    info.style.display = (e.target.value !== 'fawkes') ? 'block' : 'none';
});

document.getElementById('protectForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const method = document.getElementById('method').value;
    const fileInput = document.getElementById('imageFile');
    const statusCard = document.getElementById('statusCard');
    const statusText = document.getElementById('jobStatusText');
    const details = document.getElementById('jobDetails');

    if (!fileInput.files[0]) return;

    statusCard.style.display = 'block';
    statusText.textContent = 'Uploading...';
    details.innerHTML = '';

    const formData = new FormData();
    formData.append('image', fileInput.files[0]);

    if (method === 'fawkes') {
        // Legacy synchronous call
        try {
            const res = await fetch(`${API_BASE}/api/protect/fawkes`, { method: 'POST', body: formData });
            const data = await res.json();
            statusText.textContent = 'Completed (Fawkes)';
            details.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
            if (data.path) {
                // Assuming path is returned, normally we'd download
            }
        } catch (e) {
            statusText.textContent = 'Error';
            details.textContent = e.message;
        }
    } else {
        // Async Queue call
        formData.append('type', method);
        try {
            const res = await fetch(`${API_BASE}/api/protect/queue/add`, { method: 'POST', body: formData });

            if (!res.ok) throw new Error("Failed to add to queue");

            const job = await res.json();
            statusText.textContent = 'Queued (Waiting for Worker...)';
            pollJob(job.id);
        } catch (e) {
            statusText.textContent = 'Error Queueing';
            details.textContent = e.message;
        }
    }
});

async function pollJob(jobId) {
    const statusText = document.getElementById('jobStatusText');
    const details = document.getElementById('jobDetails');
    const pollInterval = setInterval(async () => {
        try {
            const res = await fetch(`${API_BASE}/api/protect/queue/status/${jobId}`);
            const job = await res.json();

            if (job.status === 'completed') {
                clearInterval(pollInterval);
                statusText.textContent = 'Finished!';
                details.innerHTML = `
                    <p>Protected Image Ready:</p>
                    <a href="${API_BASE}/api/protect/queue/result/${jobId}" target="_blank" class="button">Download Result</a>
                `;
            } else if (job.status === 'failed') {
                clearInterval(pollInterval);
                statusText.textContent = 'Failed';
                details.textContent = job.error || "Unknown error";
            } else if (job.status === 'processing') {
                statusText.textContent = 'Processing on GPU...';
            }
        } catch (e) {
            console.error("Poll error", e);
        }
    }, 2000);
}

// Init
checkHealth();
setInterval(checkHealth, 30000);
