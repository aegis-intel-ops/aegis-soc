const API_BASE = '';

// Check API status
async function checkStatus() {
    const status = document.getElementById('status');
    try {
        const res = await fetch(`${API_BASE}/health`);
        if (res.ok) {
            status.textContent = '● Connected';
            status.className = 'status connected';
            loadAllData();
        }
    } catch (e) {
        status.textContent = '○ Disconnected';
        status.className = 'status';
    }
}

// Load all data
async function loadAllData() {
    loadStats();
    loadClients();
    loadCases();
    loadAlerts();
}

// Load stats
async function loadStats() {
    try {
        // Clients count
        const clients = await fetch(`${API_BASE}/api/soc/clients`).then(r => r.json());
        document.getElementById('clientCount').textContent = clients.length;

        // Cases stats
        const caseStats = await fetch(`${API_BASE}/api/soc/cases/stats/overview`).then(r => r.json());
        document.getElementById('openCases').textContent = caseStats.by_status?.open || 0;

        // Alert stats
        const alertStats = await fetch(`${API_BASE}/api/soc/alerts/stats`).then(r => r.json());
        document.getElementById('unackAlerts').textContent = alertStats.unacknowledged || 0;
        document.getElementById('criticalAlerts').textContent = alertStats.by_severity?.critical || 0;
    } catch (e) {
        console.error('Error loading stats:', e);
    }
}

// Load clients
async function loadClients() {
    const list = document.getElementById('clientList');
    const select = document.getElementById('caseClient');

    try {
        const clients = await fetch(`${API_BASE}/api/soc/clients`).then(r => r.json());

        // Update list
        list.innerHTML = clients.map(c => `
            <div class="list-item" onclick="viewClient('${c.id}')">
                <div class="title">${c.name}</div>
                <div class="meta">
                    <span class="badge ${c.risk_level}">${c.risk_level}</span>
                    ${c.code_name || ''} • ${c.case_count} cases
                </div>
            </div>
        `).join('') || '<div class="list-item"><div class="meta">No clients yet</div></div>';

        // Update select dropdown
        select.innerHTML = '<option value="">No Client</option>' +
            clients.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
    } catch (e) {
        list.innerHTML = '<div class="list-item"><div class="meta">Error loading clients</div></div>';
    }
}

// Load cases
async function loadCases() {
    const list = document.getElementById('caseList');

    try {
        const cases = await fetch(`${API_BASE}/api/soc/cases?status=open`).then(r => r.json());

        list.innerHTML = cases.map(c => `
            <div class="list-item" onclick="viewCase('${c.id}')">
                <div class="title">${c.title}</div>
                <div class="meta">
                    <span class="badge ${c.status}">${c.status}</span>
                    <span class="badge ${c.priority}">${c.priority}</span>
                    ${c.alert_count} alerts
                </div>
            </div>
        `).join('') || '<div class="list-item"><div class="meta">No open cases</div></div>';
    } catch (e) {
        list.innerHTML = '<div class="list-item"><div class="meta">Error loading cases</div></div>';
    }
}

// Load alerts
async function loadAlerts() {
    const list = document.getElementById('alertList');

    try {
        const alerts = await fetch(`${API_BASE}/api/soc/alerts?acknowledged=false&limit=20`).then(r => r.json());

        list.innerHTML = alerts.map(a => `
            <div class="list-item alert-item" onclick="acknowledgeAlert('${a.id}')">
                <div class="severity ${a.severity}"></div>
                <div class="content">
                    <div class="title">${a.alert_type}</div>
                    <div class="meta">${a.message.substring(0, 100)}...</div>
                    <div class="meta">${a.source} • ${new Date(a.created_at).toLocaleString()}</div>
                </div>
            </div>
        `).join('') || '<div class="list-item"><div class="meta">No unacknowledged alerts</div></div>';
    } catch (e) {
        list.innerHTML = '<div class="list-item"><div class="meta">Error loading alerts</div></div>';
    }
}

// Modal functions
function showAddClient() {
    document.getElementById('addClientModal').classList.add('active');
}

function showAddCase() {
    document.getElementById('addCaseModal').classList.add('active');
}

function closeModal(id) {
    document.getElementById(id).classList.remove('active');
}

// Add client form
document.getElementById('addClientForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const client = {
        name: document.getElementById('clientName').value,
        code_name: document.getElementById('clientCodeName').value || null,
        email: document.getElementById('clientEmail').value || null,
        risk_level: document.getElementById('clientRisk').value
    };

    try {
        await fetch(`${API_BASE}/api/soc/clients`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(client)
        });

        closeModal('addClientModal');
        e.target.reset();
        loadAllData();
    } catch (e) {
        alert('Error adding client');
    }
});

// Add case form
document.getElementById('addCaseForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const caseData = {
        title: document.getElementById('caseTitle').value,
        description: document.getElementById('caseDescription').value || null,
        client_id: document.getElementById('caseClient').value || null,
        priority: document.getElementById('casePriority').value
    };

    try {
        await fetch(`${API_BASE}/api/soc/cases`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(caseData)
        });

        closeModal('addCaseModal');
        e.target.reset();
        loadAllData();
    } catch (e) {
        alert('Error creating case');
    }
});

// Acknowledge alert
async function acknowledgeAlert(id) {
    try {
        await fetch(`${API_BASE}/api/soc/alerts/${id}/acknowledge`, { method: 'PUT' });
        loadAllData();
    } catch (e) {
        console.error('Error acknowledging alert');
    }
}

// Acknowledge all alerts
async function acknowledgeAll() {
    try {
        const alerts = await fetch(`${API_BASE}/api/soc/alerts?acknowledged=false`).then(r => r.json());
        const ids = alerts.map(a => a.id);

        await fetch(`${API_BASE}/api/soc/alerts/bulk-acknowledge`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(ids)
        });

        loadAllData();
    } catch (e) {
        console.error('Error acknowledging alerts');
    }
}

// Placeholder view functions
function viewClient(id) { console.log('View client:', id); }
function viewCase(id) { console.log('View case:', id); }

// Init
checkStatus();
setInterval(loadAllData, 30000);
