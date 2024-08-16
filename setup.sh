docker build -t mintlify:latest -f Dockerfile .
docker run -v .:/unify-docs -p 3000:3000 -it --entrypoint bash mintlify:latest
