FROM node:20-alpine AS build

WORKDIR /app

# Copy dependency definitions
COPY package*.json ./
RUN npm ci

# Copy the rest of the app
COPY . .

# In Model 2 (Vercel), Vercel builds this automatically.
# In Model 1 (Docker Compose), we build it here.
# Allow passing VITE_API_URL at build time to bake into the static bundle.
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine
# Copy the built assets
COPY --from=build /app/dist /usr/share/nginx/html
# Copy custom nginx configuration for React SPA routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
