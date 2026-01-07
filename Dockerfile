FROM node:bookworm

WORKDIR /docs

RUN npm install -g mintlify

CMD ["mintlify", "dev"]
