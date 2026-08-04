# Marino 007 command center.
#
# Node and Python share one image on purpose: the dashboard spawns the blog
# and order scripts directly, and SQLite wants a single writer on a single
# disk. Splitting these into separate services would mean rewriting the
# control API as a job queue and moving to Postgres - a lot of machinery for
# a workload this size.

FROM node:20-slim

# Python for the ops scripts, plus the toolchain better-sqlite3 compiles against
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 \
      python3-pip \
      python3-venv \
      build-essential \
      ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# --- Python deps (own layer so JS churn doesn't rebuild them) ---
COPY requirements.txt ./
RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt
ENV PATH="/opt/venv/bin:$PATH"

# --- Node deps for the WhatsApp bridge ---
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

# --- Dashboard build ---
COPY shopify-affiliates/package.json shopify-affiliates/package-lock.json ./shopify-affiliates/
RUN cd shopify-affiliates && npm ci

COPY . .

# ARG, not ENV: an ENV would bake the placeholder into the final image as a
# working default password. If the real env var ever failed to apply, that
# placeholder would unlock a public dashboard. ARG exists only for this layer.
ARG DASHBOARD_PASSWORD=build-time-placeholder
RUN cd shopify-affiliates && npm run build

# Written state lives here, mounted as a volume in production.
ENV DATA_DIR=/data
ENV HEADLESS=1
ENV WHATSAPP_PORT=3010
ENV PORT=3003
RUN mkdir -p /data

EXPOSE 3003

CMD ["node", "supervisor.js"]
