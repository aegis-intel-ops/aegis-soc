const API_BASE = 'http://129.213.117.130:8000';

// Check API status and credits
async function checkStatus() {
    const status = document.getElementById('status');
    const credits = document.getElementById('credits');

    try {
        const res = await fetch(`${API_BASE}/api/osint/shodan/api-info`);
        const data = await res.json();

        if (data.status === 'configured') {
            status.textContent = '● Connected';
            status.className = 'status connected';
            credits.textContent = `Credits: ${data.query_credits || 0}`;
        } else if (data.status === 'not_configured') {
            status.textContent = '⚠ API Key Missing';
            status.className = 'status error';
            credits.textContent = '';
        } else {
            status.textContent = '○ Error';
            status.className = 'status error';
        }
    } catch (e) {
        status.textContent = '○ Disconnected';
        status.className = 'status error';
        credits.textContent = '';
    }
}

// Host/IP Lookup
document.getElementById('hostForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const ip = document.getElementById('hostIp').value.trim();
    const results = document.getElementById('hostResults');

    results.textContent = 'Scanning IP...';
    results.className = 'results loading';

    try {
        const res = await fetch(`${API_BASE}/api/osint/shodan/host/${ip}`);
        const data = await res.json();

        if (data.detail) {
            results.textContent = `Error: ${data.detail}`;
            results.className = 'results error';
        } else {
            // Format nicely
            let output = `IP: ${data.ip}\n`;
            output += `Organization: ${data.org || 'N/A'}\n`;
            output += `ISP: ${data.isp || 'N/A'}\n`;
            output += `Location: ${data.city || 'N/A'}, ${data.country || 'N/A'}\n`;
            output += `\nOpen Ports: ${data.ports?.join(', ') || 'None detected'}\n`;

            if (data.vulns && data.vulns.length > 0) {
                output += `\n⚠️ Vulnerabilities:\n${data.vulns.join('\n')}`;
            }

            if (data.hostnames && data.hostnames.length > 0) {
                output += `\n\nHostnames:\n${data.hostnames.join('\n')}`;
            }

            results.textContent = output;
            results.className = 'results';
        }
    } catch (e) {
        results.textContent = `Error: ${e.message}`;
        results.className = 'results error';
    }
});

// Search Database
document.getElementById('searchForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = document.getElementById('searchQuery').value.trim();
    const results = document.getElementById('searchResults');

    results.textContent = 'Searching Shodan...';
    results.className = 'results loading';

    try {
        const res = await fetch(`${API_BASE}/api/osint/shodan/search?query=${encodeURIComponent(query)}`);
        const data = await res.json();

        if (data.detail) {
            results.textContent = `Error: ${data.detail}`;
            results.className = 'results error';
        } else {
            let output = `Total Results: ${data.total}\n\n`;

            if (data.matches && data.matches.length > 0) {
                data.matches.forEach((m, i) => {
                    output += `[${i + 1}] ${m.ip}:${m.port}\n`;
                    output += `    Org: ${m.org || 'N/A'}\n`;
                    output += `    Product: ${m.product || 'N/A'} ${m.version || ''}\n`;
                    output += `    Country: ${m.country || 'N/A'}\n\n`;
                });
            } else {
                output += 'No matches found.';
            }

            results.textContent = output;
            results.className = 'results';
        }
    } catch (e) {
        results.textContent = `Error: ${e.message}`;
        results.className = 'results error';
    }
});

// DNS Lookup
document.getElementById('dnsForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const domain = document.getElementById('dnsDomain').value.trim();
    const results = document.getElementById('dnsResults');

    results.textContent = 'Resolving DNS...';
    results.className = 'results loading';

    try {
        const res = await fetch(`${API_BASE}/api/osint/shodan/dns/${domain}`);
        const data = await res.json();

        if (data.detail) {
            results.textContent = `Error: ${data.detail}`;
            results.className = 'results error';
        } else {
            let output = `DNS Resolution for: ${domain}\n\n`;
            for (const [host, ip] of Object.entries(data)) {
                output += `${host} → ${ip}\n`;
            }
            results.textContent = output;
            results.className = 'results';
        }
    } catch (e) {
        results.textContent = `Error: ${e.message}`;
        results.className = 'results error';
    }
});

// Exploit Search
document.getElementById('exploitForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = document.getElementById('exploitQuery').value.trim();
    const results = document.getElementById('exploitResults');

    results.textContent = 'Searching exploits...';
    results.className = 'results loading';

    try {
        const res = await fetch(`${API_BASE}/api/osint/shodan/exploits?query=${encodeURIComponent(query)}`);
        const data = await res.json();

        if (data.detail) {
            results.textContent = `Error: ${data.detail}`;
            results.className = 'results error';
        } else {
            let output = `Total Exploits: ${data.total}\n\n`;

            if (data.exploits && data.exploits.length > 0) {
                data.exploits.forEach((e, i) => {
                    output += `[${i + 1}] ${e.description?.substring(0, 80) || 'No description'}...\n`;
                    output += `    Source: ${e.source || 'N/A'}\n`;
                    output += `    Type: ${e.type || 'N/A'}\n`;
                    if (e.cve && e.cve.length > 0) {
                        output += `    CVE: ${e.cve.join(', ')}\n`;
                    }
                    output += '\n';
                });
            } else {
                output += 'No exploits found.';
            }

            results.textContent = output;
            results.className = 'results';
        }
    } catch (e) {
        results.textContent = `Error: ${e.message}`;
        results.className = 'results error';
    }
});

// Init
checkStatus();
setInterval(checkStatus, 60000);
