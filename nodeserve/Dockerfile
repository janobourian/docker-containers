FROM node:20-alpine
WORKDIR /usr/src/app
COPY ./app/package*.json ./
RUN npm install --only=production
COPY ./app .
USER node
EXPOSE 3000
CMD ["npm", "run", "start"]