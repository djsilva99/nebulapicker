# ----------------------------------------------------------------------
# Stage 1: Dependencies (Install all Node modules)
# ----------------------------------------------------------------------
# Use a Node base image
FROM node:21.6.1-alpine AS deps

# Set working directory inside the container
WORKDIR /app

# Copy only the package files to leverage Docker layer caching.
# If these files don't change, subsequent builds skip the 'npm install' step.
COPY package.json package-lock.json ./

# Install only production dependencies for the final image.
# We also install dev dependencies here temporarily for the build stage.
RUN npm install

# ----------------------------------------------------------------------
# Stage 2: Builder (Run 'next build')
# ----------------------------------------------------------------------
FROM node:21.6.1-alpine AS builder
WORKDIR /app

# Copy all installed dependencies from the 'deps' stage
COPY --from=deps /app/node_modules ./node_modules

# Copy the rest of the application source code
COPY . .

# Disable Next.js telemetry during the build
ENV NEXT_TELEMETRY_DISABLED 1

# Run the Next.js build command
RUN npm run build

# ----------------------------------------------------------------------
# Stage 3: Runner (The small, final production image)
# ----------------------------------------------------------------------
# Start fresh with a small, production-ready base image
FROM node:21.6.1-alpine AS runner
WORKDIR /app

# 1. Copy only necessary production dependencies
# Copy the installed node_modules from the 'deps' stage
COPY --from=deps /app/node_modules ./node_modules

# 2. Copy Next.js build output, package.json, and public assets
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/package.json ./package.json

# You may also need next.config.js or any custom server files
# COPY --from=builder /app/next.config.js ./next.config.js

# Set environment variables for runtime
ENV NODE_ENV production
ENV PORT 3000
ENV NEXT_TELEMETRY_DISABLED 1

# Expose the port Next.js runs on by default
EXPOSE 3000

# Start the Next.js server
CMD ["npm", "start"]
