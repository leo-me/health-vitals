FROM node:22-alpine

# libc6-compat — needed by some Node native modules (e.g. sharp via next/image)
RUN apk add --no-cache libc6-compat

WORKDIR /frontend

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
