FROM node:22-alpine AS builder

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .

ARG REACT_APP_BACKEND_URL=http://localhost:8000
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=builder /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
