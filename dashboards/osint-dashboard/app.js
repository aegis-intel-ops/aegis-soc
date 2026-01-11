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

// ===== SHODAN =====

// Shodan IP Lookup
document.getElementById('shodanForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const ip = document.getElementById('shodanIp').value;
    const results = document.getElementById('shodanResults');

    results.textContent = 'Scanning IP with Shodan...';
    results.classList.add('loading');

    try {
        const res = await fetch(`${API_BASE}/api/osint/shodan/host/${ip}`);
        const data = await res.json();

        if (data.detail) {
            results.textContent = `Error: ${data.detail}`;
        } else {
            results.textContent = JSON.stringify(data, null, 2);
        }
    } catch (e) {
        results.textContent = `Error: ${e.message}`;
    }
    results.classList.remove('loading');
});

// Shodan Search
document.getElementById('shodanSearchForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = document.getElementById('shodanQuery').value;
    const results = document.getElementById('shodanSearchResults');

    results.textContent = 'Searching Shodan...';
    results.classList.add('loading');

    try {
        const res = await fetch(`${API_BASE}/api/osint/shodan/search?query=${encodeURIComponent(query)}`);
        const data = await res.json();
        results.textContent = JSON.stringify(data, null, 2);
    } catch (e) {
        results.textContent = `Error: ${e.message}`;
    }
    results.classList.remove('loading');
});

// ===== SPIDERFOOT =====

// SpiderFoot Scan
document.getElementById('spiderfootForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const target = document.getElementById('spiderfootTarget').value;
    const scanType = document.getElementById('scanType').value;
    const results = document.getElementById('spiderfootResults');

    results.textContent = 'Starting SpiderFoot scan...';
    results.classList.add('loading');

    try {
        const res = await fetch(`${API_BASE}/api/osint/spiderfoot/scan`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target, scan_type: scanType })
        });
        const data = await res.json();

        results.textContent = `Scan started!\nID: ${data.scan_id}\nStatus: ${data.status}\n\nPolling for results...`;

        // Poll for completion
        pollScanStatus(data.scan_id, results);
    } catch (e) {
        results.textContent = `Error: ${e.message}`;
        results.classList.remove('loading');
    }
});

async function pollScanStatus(scanId, resultsEl) {
    let attempts = 0;
    const maxAttempts = 30;

    const poll = setInterval(async () => {
        attempts++;

        try {
            const res = await fetch(`${API_BASE}/api/osint/spiderfoot/status/${scanId}`);
            const data = await res.json();

            resultsEl.textContent = `Scan ID: ${scanId}\nStatus: ${data.status}\nProgress: ${data.progress}%\nResults: ${data.results_count}`;

            if (data.status === 'completed' || data.status === 'failed' || attempts >= maxAttempts) {
                clearInterval(poll);
                resultsEl.classList.remove('loading');

                if (data.status === 'completed') {
                    // Get full results
                    const resResults = await fetch(`${API_BASE}/api/osint/spiderfoot/results/${scanId}`);
                    const fullData = await resResults.json();
                    resultsEl.textContent = JSON.stringify(fullData, null, 2);
                }
            }
        } catch (e) {
            clearInterval(poll);
            resultsEl.textContent += `\nError: ${e.message}`;
            resultsEl.classList.remove('loading');
        }
    }, 2000);
}

// ===== ORIGINAL OSINT TOOLS =====

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
