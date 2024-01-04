FROM hub.docker.hpecorp.net/hub/node:16.14.2-alpine3.15

WORKDIR /usr/src/app

COPY package*.json app.js compose-schema.json ./

RUN npm ci --only=production

CMD ["node", "app.js"]
