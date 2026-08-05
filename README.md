# Marino 007 — AI Command Center

> **Built by Marino Santos. Powered by Marino 007. Made for the culture.**
> The AI brain behind **Los Iconos de la Bachata** — orchestrating storefront, fulfillment, messaging, marketing, and content from one place.

Marino 007 is an autonomous AI agent and operations hub for a bachata music brand. It watches the Shopify store, pushes orders to Printify, alerts the owner on WhatsApp, writes and publishes a daily blog from the brand's own photo archive, runs the affiliate program, and answers questions as a Claude-powered agent — all from a single deployable container.

Built on **Claude Sonnet 5**, with **87 skill modules** and a live command center dashboard.

---

## The System

| Subsystem | What It Does |
|---|---|
| **AI Agent** (`marino_007.py`) | Claude-powered conversational agent with tool use — brand strategy, campaign planning, content ideas, and WhatsApp sending |
| **Order Automation** (`order_automation.py`) | Checks Shopify hourly for new orders, forwards them to Printify for print-on-demand fulfillment, and alerts on WhatsApp |
| **WhatsApp Bridge** (`whatsapp_server.js`) | Baileys socket on port 3010 — QR *and* pairing-code linking, message send/receive over HTTP |
| **Blog Engine** (`blog_scheduler.py`) | Daily at 9 AM: pulls the oldest unblogged photo from Google Photos, matches Drive docs by date, researches the web, writes an 800–1200 word post with Claude, and emails the customer list |
| **Command Center** (`shopify-affiliates/`) | Next.js dashboard — system health, affiliate roster, message board, sales analytics, and one-click ops |
| **Affiliate Hub** | SQLite-backed affiliate tracking with referral sales attribution and outbound messaging |
| **Google Ads** (`google_ads_api.py`) | Campaign creation and management targeting Aventura / Latin music audiences |
| **Skills** (`skills/`) | 87 domain modules — commerce, finance, legal, music industry, social, design, and more |

---

## Architecture

Everything runs in **one container**, kept alive by `supervisor.js`. The dashboard spawns the Python scripts directly and SQLite wants a single writer on a single disk — splitting into separate services would mean a job queue and Postgres, which is a lot of machinery for this workload.

```
supervisor.js  —  restarts what dies, exits loud if it won't stay up
|
|-- whatsapp    ->  whatsapp_server.js       (Baileys, port 3010)   [critical]
|-- dashboard   ->  shopify-affiliates/      (Next.js, port 3003)   [critical]
|-- blog        ->  blog_scheduler.py        (daemon, 9 AM daily)   [optional]

order_automation.py  ->  Shopify  ->  Printify  ->  WhatsApp alert
marino_007.py        ->  Claude Sonnet 5 + tools (get_date, send_whatsapp)

/data (mounted volume)
|-- auth_info/            WhatsApp session — losing it means re-linking
|-- affiliates.db         Affiliates, messages, sales
|-- blog_tracker.json     Photos already blogged (prevents duplicates)
|-- processed_orders.json Orders already fulfilled (prevents doubles)
|-- blogs/                Generated posts
```

Those last two matter more than they look — without them a redeploy would re-send orders to Printify and re-publish blogs that already went out.

---

## Command Center

The dashboard at port `3003` is password-gated and has four tabs:

| Tab | What's There |
|---|---|
| **Command** | Live health for all 7 systems, WhatsApp linking (QR or pairing code), and an ops console for read-only checks |
| **Affiliates** | Affiliate roster, referral codes, and performance |
| **Messages** | Outbound message board to affiliates |
| **Sales** | Revenue and attribution charts |

**Monitored systems:** WhatsApp Bridge · Order Automation · Shopify Store · Printify Fulfillment · Blog Engine · Google Ads · Affiliate Hub

---

## Core Files

| File | Purpose |
|---|---|
| `marino_007.py` | The agent — system prompt, tool loop, Claude integration |
| `MEMORY.md` | Long-term memory — creator, brand, family, standing context |
| `supervisor.js` | Process supervisor for the container |
| `paths.py` | Where mutable state goes — project folder locally, `/data` in production |
| `start_marino_007.py` | Local launcher for WhatsApp + orders + blog |
| `start_command_center.ps1` | Windows one-command startup (bridge, dashboard, tunnel) |
| `Dockerfile` / `render.yaml` | One-container build and Render blueprint |
| `DEPLOY.md` | Full deployment walkthrough |
| `skills/` | 87 skill modules |

---

## Tech Stack

| Layer | Technology |
|---|---|
| AI Core | Claude Sonnet 5 (Anthropic Python SDK) |
| Backend | Python 3.10+ — 26 modules |
| Bridge | Node.js 20 + Baileys (`@whiskeysockets/baileys`) + Express |
| Dashboard | Next.js 16 · React 19 · TypeScript · Recharts |
| Database | SQLite (`better-sqlite3`) |
| Auth | JWT + bcrypt, password-gated sessions |
| Commerce | Shopify Admin API (OAuth) + Printify |
| Content | Google Photos · Google Drive · DuckDuckGo · Gmail SMTP |
| Marketing | Google Ads API |
| Deploy | Docker → Render (Starter plan, 1 GB persistent disk) |

---

## Brand

- **Primary Color:** `#d4af37` (Los Iconos Gold)
- **Theme:** Dark (`#05060d` base)
- **Brand:** Los Iconos de la Bachata — [losiconosdelabachata.com](https://losiconosdelabachata.com)
- **Identity:** Timeless music, timeless stories. Confident, creative, culturally rooted.
- **Credit:** Built by and credited to **Marino Santos**

---

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 20+
- Anthropic API key
- Shopify Admin API credentials
- A dedicated phone number for the WhatsApp bridge

### Install

```bash
git clone https://github.com/losiconosdelabachata-star/Marino-007-.git
cd Marino-007-
pip install -r requirements.txt
npm install
cd shopify-affiliates && npm install && cd ..
```

### Environment Setup

```bash
cp .env.example .env
```

Fill in your real values. `.env` is gitignored — keep it that way.

### Run

**Everything at once (Windows):**

```bash
powershell -ExecutionPolicy Bypass -File start_command_center.ps1
```

**Just the agent:**

```bash
python marino_007.py
```

**Individual services:**

```bash
node whatsapp_server.js
python order_automation.py
python blog_scheduler.py
```

Then open **http://localhost:3003** and log in.

---

## Deploy

Render Dashboard → **New** → **Blueprint** → point at this repo. `render.yaml` prompts for every secret.

Two things a server can't do for itself:

1. **Google refresh tokens** — a server has no browser and can never click "Allow". Run `python get_refresh_token.py` locally once and paste the output into Render.
2. **WhatsApp linking** — the session doesn't transfer from your laptop. Link once from the Command tab; it survives redeploys because the session lives on the mounted disk.

Full walkthrough in **[DEPLOY.md](DEPLOY.md)**.

---

## Skills

87 modules across every domain the brand touches:

**Commerce & Ops** — shopify · shopify-ad-apps · stripe-payments · klaviyo · task-manager · calendar-manager · api-gateway · healthcheck

**Marketing & Social** — meta-ads · tiktok-ads · google-ads · google-analytics · genviral-social-media · social-media-scheduler · influencer-marketing · pr-press-outreach · linktree · simplified-social-media

**Music Industry** — music-industry-manager · music-manager-pro · distrokid · spotify-for-artists · suno-ai · ai-podcast-creation · elevenlabs · voice-message

**Creative** — canva · capcut · graphic-design-mastery · image-generation · heygen-ai · higgsfield-ai · creatify-ai · gamma-ai · claude-design · hyperframes

**Finance & Investing** — investing-analyst · us-stock-analysis · stock-strategy-backtester · stock-study · market-sentiment-pulse · real-estate-investing · storyclaw-alpaca-trading · trading-devbox · rollhub-analyst · credit · credit-repair-skill · card-optimizer · betting

**Business & Legal** — business · business-plan · business-model-canvas · proposal-writer · grant · grant-writing-framework · nyc-funds-finder · legal-ai-counsel · ai-legal-standard-v2 · normieclaw-legal-docs-pro · fiverr

**Health & Wellbeing** — therapy · mens-mental-health · nutritionist · training-and-nutrition-coach · sensual-makeup

**Dev & Agent** — claude-code · claude-cowork · coding-agent · github · gh-issues · node-connect · openai-api · cybersecurity · skill-creator · self-improving-agent · proactive-agent · cross-session-tasks · session-logs · summarize · document-reader

**Platforms** — notion · slack · discord · wix · weather · event-management · real-estate-skill

---

## Roadmap

- [x] Claude-powered agent with persistent memory
- [x] 87 skill modules loaded
- [x] WhatsApp bridge with QR *and* pairing-code linking
- [x] Shopify OAuth + Printify fulfillment, duplicate-safe
- [x] Blog engine — Photos + Drive + web research → Claude → HTML + email
- [x] Command center dashboard with live system health
- [x] Password-gated auth, all credentials moved to environment
- [x] Containerized, one-command deploy to Render
- [ ] Restore Google Photos access (blocked on Google One billing)
- [ ] Live Printify API key (currently a placeholder)
- [ ] Approved Google Ads developer token
- [ ] Sub-agents — a dedicated agent per skill module
- [ ] Serve individuals and corporations across the full skill suite

---

## Known Gaps

| Gap | Status |
|---|---|
| Google Photos returns 403 | Blocked on Google One billing — blog engine idles until resolved |
| Printify API key | Placeholder — order automation reports "setup needed" |
| Google Ads | Needs an approved developer token |
| Gmail | Needs an app password, not the account password |

---

## License & Brand

<img src="marino-007-avatar.png" alt="Marino 007" width="120" height="120">

### Marino 007 | Built by Marino Santos for Los Iconos de la Bachata

**© 2026 Marino Santos. All rights reserved.**

This project is proprietary and protected under copyright law. It is part of the Los Iconos de la Bachata ecosystem, with full intellectual property rights reserved by Marino Santos.

### License Details

- **Type:** Proprietary — All Rights Reserved
- **Owner:** Marino Santos
- **Brand:** Los Iconos de la Bachata
- **Status:** Protected and Confidential

### Key Rights

- **All intellectual property retained**
- **Reproduction prohibited without permission**
- **Distribution rights reserved**
- **Derivative works not permitted**
- **Commercial use requires authorization**

### Attribution

When referencing this software, please include:
- Marino 007
- Marino Santos
- Los Iconos de la Bachata

### Inquiries

For licensing, partnerships, or usage permissions:
Email: **losiconosdelabachata@gmail.com**

---

**Learn more:** [Full License](LICENSE) · [Deployment Guide](DEPLOY.md) · [Blog Engine](BLOG_README.md)

**Los Iconos de la Bachata** — *Timeless Music, Timeless Stories*
