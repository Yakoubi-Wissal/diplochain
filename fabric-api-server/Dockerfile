FROM node:18-slim

WORKDIR /app

# Install docker-cli to allow the container to run docker commands (osnadmin, etc.)
RUN apt-get update && apt-get install -y docker.io curl && rm -rf /var/lib/apt/lists/*

COPY package*.json ./
RUN npm install

COPY . .

# Environment variables will be overridden by docker-compose
ENV PORT=4001
ENV PG_HOST=postgres
ENV COUCHDB_URL=http://admin:diplochain_couch_2025@couchdb0.diplochain.local:5984

EXPOSE 4001

CMD ["node", "index.js"]
