FROM node:22-slim AS base
WORKDIR /app

# ---- development: hot-reload por volumen (ver docker-compose.yml) ----
FROM base AS development
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
CMD ["npm", "run", "dev"]

# ---- production: build estático + servidor mínimo ----
FROM base AS builder
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM base AS production
ENV NODE_ENV=production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
RUN useradd --system --create-home appuser && chown -R appuser /app
USER appuser
CMD ["npm", "start"]
