# Stage 1: Build
FROM node:22-alpine AS builder

WORKDIR /app

# Copy dependency files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Fix executable permissions (prevents Error 126)
RUN chmod -R +x node_modules/.bin

# Build arguments with default fallback
ARG VITE_API_BASE_URL=https://resume-backend-948277799081.us-central1.run.app
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Build the application
RUN npm run build

# Debug: List built files
RUN echo "=== Built files ===" && ls -la dist/ && ls -la dist/assets/ || true

# Stage 2: Production
FROM nginx:alpine

# Install curl for health checks
RUN apk add --no-cache curl

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Remove default nginx config to avoid conflicts
RUN rm -f /etc/nginx/conf.d/default.conf.bak 2>/dev/null || true

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Debug: Verify files were copied
RUN echo "=== Files in nginx html directory ===" && ls -la /usr/share/nginx/html/ && ls -la /usr/share/nginx/html/assets/ || true

# Create a fallback health check file
RUN echo "healthy" > /usr/share/nginx/html/health.txt

# Expose port 8080 (Cloud Run requirement)
EXPOSE 8080

# Health check for Cloud Run
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
