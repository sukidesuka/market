FROM node:12-alpine AS builder
COPY package.json /app/
WORKDIR /app
RUN npm install
COPY . /app
RUN npm run build

FROM nginx
COPY --from=builder /app/dist /usr/share/nginx/html