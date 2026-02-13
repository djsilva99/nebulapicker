# Global build argument to receive the internal API host from docker-compose.
ARG API_DESTINATION

# ----------------------------------------------------------------------
# Stage 1: Dependencies (Install all Node modules)
# ----------------------------------------------------------------------
# Use a Node base image
FROM node:21.6.1-alpine AS deps

# Set working directory inside the container
WORKDIR /app

# Copy only the package files to leverage Docker layer caching.
COPY package.json package-lock.json ./

# Install all dependencies (production and dev for the builder)
RUN npm install

# ----------------------------------------------------------------------
# Stage 2: Builder (Run 'next build')
# ----------------------------------------------------------------------
FROM node:21.6.1-alpine AS builder
WORKDIR /app

# Re-declare ARG to inherit the value from the global ARG
ARG API_DESTINATION

# Copy all installed dependencies from the 'deps' stage
COPY --from=deps /app/node_modules ./node_modules

# Copy the rest of the application source code
COPY . .

# Disable Next.js telemetry during the build
ENV NEXT_TELEMETRY_DISABLED 1

# Inject API_URL environment variable during the build.
#ENV API_URL=${API_DESTINATION}

# Run the Next.js build command
RUN npm run build

# ----------------------------------------------------------------------
# Stage 3: Runner (The small, final production image)
# ----------------------------------------------------------------------
# Start fresh with a small, production-ready base image
FROM node:21.6.1-alpine AS runner
WORKDIR /app

# Copy the installed node_modules from the 'deps' stage
COPY --from=deps /app/node_modules ./node_modules

# Copy Next.js build output, package.json, and public assets
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/package.json ./package.json

# Set environment variables for runtime
ENV API_URL=http://api:8000
ENV NODE_ENV production
# Set the production port (3000 is standard for Next.js)
ENV PORT 3000
ENV NEXT_TELEMETRY_DISABLED 1

# Expose the port Next.js runs on by default
EXPOSE 3000

# Start the Next.js server
CMD ["npm", "start"]
