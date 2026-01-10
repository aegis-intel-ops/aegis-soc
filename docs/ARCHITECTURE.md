# Aegis SOC - Architecture

> **Living Document** - Last Updated: 2026-01-10

## Services Overview

| Service | API Port | Dashboard | Status |
|---------|----------|-----------|--------|
| **OSINT** | 8000 | 8200 | ✅ Live |
| **Shodan** | - | 8201 | ✅ Live |
| **AI Protection** | 8010 | 8210 | ✅ Live |
| **Voice Protection** | 8020 | 8220 | ✅ Live |
| **SpiderFoot** | 5001 | - | ✅ Live |
| **n8n Automation** | 5678 | - | ✅ Live |

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

## 4. SpiderFoot (Standalone)
**Port:** 5001

Full OSINT automation platform with web UI.
Access directly at: http://129.213.117.130:5001

---

## Infrastructure

**Server:** Oracle Cloud Ampere (4 OCPU, 24GB RAM)  
**IP:** 129.213.117.130  
**OS:** Ubuntu 22.04 ARM

### Port Allocation
| Range | Purpose |
|-------|---------|
| 5001 | SpiderFoot |
| 5678 | n8n |
| 8000-8009 | OSINT |
| 8010-8019 | AI Protection |
| 8020-8029 | Voice Protection |
| 8200-8299 | Dashboards |

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
