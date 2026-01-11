# Aegis SOC - Architecture

> **Living Document** - Last Updated: 2026-01-10

## Services Overview

| Service | Internal Port | Access (Subdomain) | Status |
|---------|---------------|--------------------|--------|
| **Gateway** | 80 | `http://129.213...` | ✅ Live |
| **SOC Core** | 8030 | `soc.` | ✅ Live |
| **OSINT** | 8000 | `osint.` | ✅ Live |
| **Shodan** | - | `shodan.` | ✅ Live |
| **AI Protection** | 8010 | `ai.` | ✅ Live |
| **Voice Protection** | 8020 | `voice.` | ✅ Live |
| **SpiderFoot** | 5001 | `spiderfoot.` | ✅ Live |

---

## 1. OSINT Service
**Port:** 8000 | **Dashboard:** 8200

### Core Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/osint/recon` | POST | Domain recon (TheHarvester) |
| `/api/osint/email/{email}` | GET | Email lookup |
| `/api/osint/username/{username}` | GET | Username search |

### Shodan Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/osint/shodan/host/{ip}` | GET | IP information |
| `/api/osint/shodan/search` | GET | Search Shodan database |
| `/api/osint/shodan/dns/{domain}` | GET | DNS resolution |
| `/api/osint/shodan/exploits` | GET | Exploit search |
| `/api/osint/shodan/api-info` | GET | API credits info |

### SpiderFoot Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/osint/spiderfoot/scan` | POST | Start OSINT scan |
| `/api/osint/spiderfoot/status/{id}` | GET | Scan status |
| `/api/osint/spiderfoot/results/{id}` | GET | Scan results |
| `/api/osint/spiderfoot/modules` | GET | List modules |

---

## 2. AI Protection Service
**Port:** 8010 | **Dashboard:** 8210

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/protect/fawkes` | POST | Face cloaking |
| `/api/protect/status/{job_id}` | GET | Job status |
| `/api/protect/download/{job_id}` | GET | Download result |

**Coming Soon:** MIST v2, PhotoGuard (Colab GPU)

---

## 3. Voice Protection Service
**Port:** 8020 | **Dashboard:** 8220

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/voice/analyze` | POST | AI audio detection |
| `/api/voice/watermark` | POST | Add watermark |
| `/api/voice/verify/{id}` | GET | Verify watermark |
| `/api/voice/download/{id}` | GET | Download watermarked |

---

## 4. SOC Core Service (NEW)
**Port:** 8030 | **Dashboard:** 8230

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/soc/clients` | CRUD | Client management |
| `/api/soc/cases` | CRUD | Case tracking workflow |
| `/api/soc/alerts` | CRUD | Alert system |

---

## 5. Unified Portal
**Port:** 8080

Central dashboard linking all services.

---

## 6. SpiderFoot (Standalone)
**Port:** 5001

Full OSINT automation platform with web UI.
Access via: `http://spiderfoot.129.213.117.130.nip.io`

---

## Infrastructure

**Server:** Oracle Cloud Ampere (4 OCPU, 24GB RAM)  
**IP:** 129.213.117.130  
**OS:** Ubuntu 22.04 ARM

### Port Allocation
| Range | Purpose | Access |
|-------|---------|--------|
| 80 | Nginx Gateway | **Public** |
| 5000-8999 | Internal Services | **Blocked** (Internal Network Only) |

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SHODAN_API_KEY` | Optional | Shodan API key |
| `SPIDERFOOT_URL` | Auto | Set by docker-compose |

---

## Changelog

| Date | Changes |
|------|---------|
| 2026-01-09 | Initial setup, OSINT service |
| 2026-01-09 | AI Protection service + dashboard |
| 2026-01-10 | Voice Protection service + dashboard |
| 2026-01-10 | Shodan integration |
| 2026-01-10 | SpiderFoot integration |
| 2026-01-10 | SOC Core Service |
| 2026-01-10 | Unified Dashboard |
