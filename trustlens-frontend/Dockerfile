# Build stage
FROM node:20-alpine AS build
WORKDIR /app

# Copy package files and install dependencies deterministically
COPY package*.json ./
RUN npm ci

# Copy source code and build
COPY . .
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

# Production stage: Nginx
FROM nginx:stable-alpine

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from Vite (outputs to 'dist')
COPY --from=build /app/dist /usr/share/nginx/html

# Create a health check endpoint (empty static file)
RUN touch /usr/share/nginx/html/healthz

# Expose port 80
EXPOSE 80

# Start Nginx (keeps process in foreground for Cloud Run)
CMD ["nginx", "-g", "daemon off;"]
