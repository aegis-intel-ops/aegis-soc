# Aegis SOC Platform

A comprehensive Security Operations Center (SOC) platform for VIP protection services.

## Services

| Service | Port | Dashboard | Description |
|---------|------|-----------|-------------|
| OSINT | 8000 | 8200 | Domain recon, email/username lookup |
| AI Protection | 8010 | 8210 | Fawkes face cloaking, MIST v2, PhotoGuard |
| Voice Protection | 8020 | 8220 | AI audio detection, watermarking |
| n8n | 5678 | - | Workflow automation |

## Quick Start

```bash
# Clone the repo
git clone https://github.com/aegis-intel-ops/aegis-soc.git
cd aegis-soc

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Oracle Server                         │
│                  129.213.117.130                         │
├─────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────────┐  ┌─────────────────┐      │
│  │  OSINT  │  │ AI Protect  │  │ Voice Protect   │      │
│  │  :8000  │  │   :8010     │  │     :8020       │      │
│  └─────────┘  └─────────────┘  └─────────────────┘      │
│  ┌─────────┐  ┌─────────────┐  ┌─────────────────┐      │
│  │Dashboard│  │  Dashboard  │  │   Dashboard     │      │
│  │  :8200  │  │   :8210     │  │     :8220       │      │
│  └─────────┘  └─────────────┘  └─────────────────┘      │
└─────────────────────────────────────────────────────────┘
```

## License

Private - Aegis Intel Ops
