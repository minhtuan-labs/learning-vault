# Build stage
FROM node:20-alpine as builder

WORKDIR /app

# Accept API URL as build argument (default to localhost for local dev)
ARG NEXT_PUBLIC_API_URL=http://localhost:8100/api/v1
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# Copy package files
COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./

# Install dependencies
RUN npm install --frozen-lockfile --legacy-peer-deps

# Copy source code
COPY . .

# Build Next.js application
RUN npm run build

# Runtime stage
FROM node:20-alpine

WORKDIR /app

# Install curl for health checks
RUN apk add --no-cache curl

# Copy package files from builder
COPY --from=builder /app/package.json /app/package-lock.json* ./

# Install only production dependencies
RUN npm ci --omit=dev --legacy-peer-deps

# Copy built application from builder
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY next.config.js .

# Create non-root user for security
RUN addgroup -g 1001 appuser && adduser -D -u 1001 -G appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD curl -f http://localhost:3000 || exit 1

# Expose port
EXPOSE 3000

# Run Next.js in production mode
CMD ["npm", "start"]
