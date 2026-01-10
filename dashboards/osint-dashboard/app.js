const API_BASE = 'http://129.213.117.130:8000';

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

// Domain Recon
document.getElementById('reconForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const domain = document.getElementById('domain').value;
    const results = document.getElementById('reconResults');

    results.textContent = 'Running reconnaissance...';
    results.classList.add('loading');

    try {
        const res = await fetch(`${API_BASE}/api/osint/recon`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ domain })
        });
        const data = await res.json();
        results.textContent = JSON.stringify(data, null, 2);
    } catch (e) {
        results.textContent = `Error: ${e.message}`;
    }
    results.classList.remove('loading');
});

// Email Lookup
document.getElementById('emailForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const results = document.getElementById('emailResults');

    results.textContent = 'Looking up email...';
    results.classList.add('loading');

    try {
        const res = await fetch(`${API_BASE}/api/osint/email/${encodeURIComponent(email)}`);
        const data = await res.json();
        results.textContent = JSON.stringify(data, null, 2);
    } catch (e) {
        results.textContent = `Error: ${e.message}`;
    }
    results.classList.remove('loading');
});

// Username Search
document.getElementById('usernameForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const results = document.getElementById('usernameResults');

    results.textContent = 'Searching username...';
    results.classList.add('loading');

    try {
        const res = await fetch(`${API_BASE}/api/osint/username/${encodeURIComponent(username)}`);
        const data = await res.json();
        results.textContent = JSON.stringify(data, null, 2);
    } catch (e) {
        results.textContent = `Error: ${e.message}`;
    }
    results.classList.remove('loading');
});

// Init
checkHealth();
setInterval(checkHealth, 30000);
