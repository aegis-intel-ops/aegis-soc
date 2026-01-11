# Aegis SOC Platform

A comprehensive Security Operations Center (SOC) platform for VIP protection services.

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/aegis-intel-ops/aegis-soc.git
cd aegis-soc

# Set environment variables
echo "SHODAN_API_KEY=your-key-here" > .env

# Start all services
docker compose up -d

# Generate Admin Password (if not done)
# Default is 'AegisSec2026!'
# To change:
docker run --entrypoint htpasswd httpd:alpine -Bbn newuser newpassword > services/gateway/.htpasswd
docker compose restart gateway


# Check status
docker compose ps
```

## 📊 Services

| Service | Port | Description |
|---------|------|-------------|
| **Gateway (Nginx)** | **80** | Single secure entry point with Basic Auth |
| **Unified Portal** | Internal | Central landing page |
| **SOC Core API** | 8030 | Client, Case, and Alert Management |
| **OSINT API** | 8000 | Intelligence gathering (Shodan, SpiderFoot, TheHarvester) |
| **AI Protection** | 8010 | Fawkes face cloaking, image protection |
| **Voice Protection** | 8020 | AI audio detection, watermarking |
| **SpiderFoot** | 5001 | Full OSINT automation (100+ sources) |
| **n8n** | 5678 | Workflow automation |

### Dashboards (Secured behind Gateway)
Access via `http://<subdomain>.129.213.117.130.nip.io`

| Dashboard | Subdomain |
|-----------|-----------|
| **Unified Portal** | `129.213...` (Root) |
| SOC Dashboard | `soc.` |
| OSINT | `osint.` |
| Shodan | `shodan.` |
| AI Protection | `ai.` |
| Voice Protection | `voice.` |
| SpiderFoot | `spiderfoot.` |
| n8n | `n8n.` |

**Credentials:** Admin / (assigned during deployment)

## 🔍 OSINT Endpoints

### Shodan (`/api/osint/shodan/`)
```bash
# Host information
GET /api/osint/shodan/host/{ip}

# Search database
GET /api/osint/shodan/search?query=apache+country:US

# DNS lookup
GET /api/osint/shodan/dns/{domain}

# Check API credits
GET /api/osint/shodan/api-info
```

### SpiderFoot (`/api/osint/spiderfoot/`)
```bash
# Start scan
POST /api/osint/spiderfoot/scan
Body: {"target": "example.com", "scan_type": "all"}

# Check status
GET /api/osint/spiderfoot/status/{scan_id}

# Get results
GET /api/osint/spiderfoot/results/{scan_id}
```

### Core OSINT (`/api/osint/`)
```bash
# Domain recon
POST /api/osint/recon
Body: {"domain": "example.com"}

# Email lookup
GET /api/osint/email/{email}

# Username search
GET /api/osint/username/{username}
```

## 🛡️ AI Protection Endpoints

```bash
# Protect image with Fawkes
POST /api/protect/fawkes
Body: multipart/form-data with image file

# Check job status
GET /api/protect/status/{job_id}
```

## 🎙️ Voice Protection Endpoints

```bash
# Analyze audio for AI detection
POST /api/voice/analyze
Body: multipart/form-data with audio file

# Add watermark
POST /api/voice/watermark
Body: multipart/form-data with audio file

# Verify watermark
GET /api/voice/verify/{watermark_id}
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Oracle Server (ARM)                       │
│                    129.213.117.130                           │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────┐  ┌─────────────┐  ┌─────────────────┐        │
│  │   OSINT   │  │ AI Protect  │  │ Voice Protect   │        │
│  │   :8000   │  │   :8010     │  │     :8020       │        │
│  │  Shodan   │  │   Fawkes    │  │  AI Detection   │        │
│  │ SpiderFoot│  │             │  │  Watermarking   │        │
│  └───────────┘  └─────────────┘  └─────────────────┘        │
│                                                              │
│  ┌───────────┐  ┌─────────────┐  ┌─────────────────┐        │
│  │   OSINT   │  │  AI Protect │  │ Voice Protect   │        │
│  │ Dashboard │  │  Dashboard  │  │   Dashboard     │        │
│  │   :8200   │  │   :8210     │  │     :8220       │        │
│  └───────────┘  └─────────────┘  └─────────────────┘        │
│                                                              │
│  ┌───────────┐  ┌─────────────┐  ┌─────────────────┐        │
│  │  Shodan   │  │ SpiderFoot  │  │      n8n        │        │
│  │ Dashboard │  │     UI      │  │   Automation    │        │
│  │   :8201   │  │   :5001     │  │     :5678       │        │
│  └───────────┘  └─────────────┘  └─────────────────┘        │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    Unified Portal                       │  │
│  │                        :8080                            │  │
│  └─────────────────────────────────────────────────────────┘  │
│          │                 │                 │                │
│    ┌───────────┐     ┌───────────┐     ┌───────────┐          │
│    │ SOC Core  │     │ SOC Dash  │     │ OSINT ... │          │
│    │   :8030   │     │   :8230   │     │           │          │
│    └───────────┘     └───────────┘     └───────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
aegis-soc/
├── services/
│   ├── soc-core/        # NEW - Clients, Cases, Alerts
│   ├── osint/           # OSINT API (Shodan, SpiderFoot, TheHarvester)
│   ├── ai-protect/      # AI Protection (Fawkes)
│   ├── voice-protect/   # Voice Protection
│   └── spiderfoot/      # SpiderFoot container
├── dashboards/
│   ├── main-dashboard/  # Unified Portal
│   ├── soc-dashboard/   # SOC Mgmt UI
│   ├── osint-dashboard/
│   ├── shodan-dashboard/
│   ├── ai-protect-dashboard/
│   └── voice-protect-dashboard/
├── colab/               # GPU notebooks (MIST, PhotoGuard)
├── docker-compose.yml
└── README.md
```

## 🔐 Environment Variables

| Variable | Description |
|----------|-------------|
| `SHODAN_API_KEY` | Shodan API key (get free at https://account.shodan.io) |

## 📋 Roadmap

- [x] OSINT Service with TheHarvester
- [x] Shodan integration + Dashboard
- [x] SpiderFoot integration
- [x] AI Protection (Fawkes)
- [x] Voice Protection (Watermarking)
- [x] SOC Core Service (alerts, clients, cases)
- [x] Unified Portal
- [ ] MIST v2 / PhotoGuard (Colab GPU)
- [ ] Voice ML models (AntiFake)

## 📄 License

Private - Aegis Intel Ops
