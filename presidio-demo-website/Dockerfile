FROM node:8.14.0-alpine AS build

ADD . /app
WORKDIR /app

RUN npm install && \
    npm run build

FROM node:8.14.0-alpine

COPY --from=build /app/build /app
RUN npm install -g serve

CMD ["serve","-s","app"]