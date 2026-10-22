# stage 1: build the vue app
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# stage 2: serve the built files and hand /api to the backend
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
# print the url so whoever runs compose knows where to look
CMD ["sh", "-c", "echo ''; echo '>>> AI Health Coach is ready: open http://localhost:5173'; echo ''; exec nginx -g 'daemon off;'"]