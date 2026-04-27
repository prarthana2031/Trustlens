# Stage 1: Build the frontend
FROM node:22-alpine AS build

WORKDIR /app

# Copy dependency files first for caching
COPY package*.json ./

# Use 'ci' to clean install dependencies. 
# This is crucial to fix your #module-sync-enabled error, 
# as it ensures a pristine node_modules folder.
RUN npm ci

# Copy the rest of the source code
COPY . .

# Set build arguments and env variables BEFORE the build
ARG REACT_APP_API_BASE_URL
ENV VITE_API_BASE_URL=$REACT_APP_API_BASE_URL

# Build the app once. 
# We removed the redundant chmod and double-build commands.
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:stable-alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built files from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
