# --- Stage 1: Build the React App ---
FROM node:18-alpine as build

WORKDIR /app

# Copy package.json and install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source code and build
COPY . .
RUN npm run build

# --- Stage 2: Serve with Nginx ---
FROM nginx:alpine

# Copy the built files from Stage 1 to Nginx's html folder
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80 (Standard web port)
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]