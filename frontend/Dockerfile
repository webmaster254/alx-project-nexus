# Multi-stage build for production
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Copy source code
COPY . .

# Build the application
ARG NODE_ENV=production
ARG VITE_API_BASE_URL
ARG VITE_APP_ENVIRONMENT
ARG VITE_SENTRY_DSN
ARG VITE_GOOGLE_ANALYTICS_ID

RUN npm run build:prod

# Production stage with nginx
FROM nginx:alpine AS production

# Copy custom nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built application
COPY --from=builder /app/dist /usr/share/nginx/html

# Add security headers
COPY --from=builder /app/public/_headers /usr/share/nginx/html/_headers

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]