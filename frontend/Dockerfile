FROM node:16

WORKDIR /app

COPY package.json yarn.lock ./

RUN yarn install --frozen-lockfile

COPY . .

RUN yarn build

RUN yarn global add serve

CMD ["serve", "-s", "build", "-l", "3000"]