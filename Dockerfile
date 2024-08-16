FROM node:bookworm

WORKDIR /unify-docs

RUN npm install -g mintlify

CMD ["mintlify", "dev"]
