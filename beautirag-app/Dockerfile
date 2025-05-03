# Use an official Node.js runtime as a parent image
FROM node:20-alpine AS base

WORKDIR /app

# Install dependencies stage
FROM base AS deps
COPY package.json package-lock.json* ./
RUN npm install

# Build stage
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Set NEXT_TELEMETRY_DISABLED to 1 to   
ENV NEXT_TELEMETRY_DISABLED 1

RUN npm run build

# Production stage
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Automatically leverage output traces to reduce image size
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static


USER nextjs

EXPOSE 3000

ENV PORT 3000
# set hostname to 0.0.0.0
ENV HOST 0.0.0.0
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]

